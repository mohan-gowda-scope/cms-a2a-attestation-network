#!/usr/bin/env python3
"""
Shadow Deployment Orchestrator for CMS A2A Multi-Agent System

This script manages the shadow deployment lifecycle:
1. Publishes new Lambda versions
2. Updates shadow alias to new version
3. Gradually shifts traffic from production to shadow
4. Monitors metrics and automatically rolls back on errors
5. Promotes shadow to production on success

Usage:
    python deploy_shadow.py --agent provider --version 42 --traffic-split 10
    python deploy_shadow.py --all-agents --auto-promote
"""

import argparse
import boto3
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS Clients
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
codedeploy = boto3.client('codedeploy')

# Configuration
PROJECT_NAME = "cms-a2a-attestation"
DEPLOYMENT_STATE_TABLE = f"{PROJECT_NAME}-deployment-state"
AGENT_LIST = [
    "provider", "clearinghouse", "cms", "payer", "pbm",
    "lab", "auditor", "credentialing", "patient", "research", "voice"
]


@dataclass
class DeploymentMetrics:
    """Metrics for comparing shadow vs production"""
    error_count: int
    avg_duration_ms: float
    invocation_count: int
    throttle_count: int


class ShadowDeploymentOrchestrator:
    """Orchestrates shadow deployments with automated monitoring and rollback"""

    def __init__(self, project_name: str = PROJECT_NAME):
        self.project_name = project_name
        self.state_table = dynamodb.Table(DEPLOYMENT_STATE_TABLE)

    def get_function_name(self, agent: str) -> str:
        """Get Lambda function name for agent"""
        return f"{self.project_name}-{agent}-aws"

    def publish_new_version(self, agent: str, description: str = None) -> str:
        """Publish a new Lambda version"""
        function_name = self.get_function_name(agent)
        
        logger.info(f"Publishing new version for {function_name}...")
        
        response = lambda_client.publish_version(
            FunctionName=function_name,
            Description=description or f"Shadow deployment {datetime.utcnow().isoformat()}"
        )
        
        version = response['Version']
        logger.info(f"Published version {version} for {function_name}")
        return version

    def update_alias(self, agent: str, alias: str, version: str, 
                     routing_config: Optional[Dict] = None) -> None:
        """Update Lambda alias to point to new version"""
        function_name = self.get_function_name(agent)
        
        logger.info(f"Updating alias '{alias}' for {function_name} to version {version}...")
        
        params = {
            'FunctionName': function_name,
            'Name': alias,
            'FunctionVersion': version
        }
        
        if routing_config:
            params['RoutingConfig'] = routing_config
        
        lambda_client.update_alias(**params)
        logger.info(f"Updated alias '{alias}' successfully")

    def get_alias_info(self, agent: str, alias: str) -> Dict:
        """Get current alias configuration"""
        function_name = self.get_function_name(agent)
        
        response = lambda_client.get_alias(
            FunctionName=function_name,
            Name=alias
        )
        return response

    def shift_traffic(self, agent: str, shadow_version: str, 
                     traffic_percentage: int) -> None:
        """
        Shift traffic from production to shadow version
        
        Args:
            agent: Agent name
            shadow_version: Shadow Lambda version
            traffic_percentage: Percentage of traffic to route to shadow (0-100)
        """
        function_name = self.get_function_name(agent)
        
        logger.info(f"Shifting {traffic_percentage}% traffic to shadow version {shadow_version}...")
        
        # Get current production version
        prod_alias = self.get_alias_info(agent, 'production')
        prod_version = prod_alias['FunctionVersion']
        
        # Update production alias with traffic routing
        routing_config = {
            'AdditionalVersionWeights': {
                shadow_version: traffic_percentage / 100.0
            }
        }
        
        self.update_alias(agent, 'production', prod_version, routing_config)
        logger.info(f"Traffic shift complete: {100-traffic_percentage}% → v{prod_version}, {traffic_percentage}% → v{shadow_version}")

    def get_metrics(self, agent: str, alias: str, 
                   start_time: datetime, end_time: datetime) -> DeploymentMetrics:
        """Get CloudWatch metrics for a Lambda alias"""
        function_name = self.get_function_name(agent)
        resource = f"{function_name}:{alias}"
        
        # Query CloudWatch metrics
        metrics = {
            'Errors': 0,
            'Duration': 0.0,
            'Invocations': 0,
            'Throttles': 0
        }
        
        for metric_name in metrics.keys():
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'FunctionName', 'Value': function_name},
                    {'Name': 'Resource', 'Value': resource}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=['Sum'] if metric_name != 'Duration' else ['Average']
            )
            
            if response['Datapoints']:
                stat = 'Sum' if metric_name != 'Duration' else 'Average'
                metrics[metric_name] = sum(dp[stat] for dp in response['Datapoints'])
        
        return DeploymentMetrics(
            error_count=int(metrics['Errors']),
            avg_duration_ms=metrics['Duration'],
            invocation_count=int(metrics['Invocations']),
            throttle_count=int(metrics['Throttles'])
        )

    def compare_metrics(self, agent: str, duration_minutes: int = 15) -> Dict:
        """Compare shadow vs production metrics"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=duration_minutes)
        
        logger.info(f"Comparing metrics for {agent} over last {duration_minutes} minutes...")
        
        prod_metrics = self.get_metrics(agent, 'production', start_time, end_time)
        shadow_metrics = self.get_metrics(agent, 'shadow', start_time, end_time)
        
        comparison = {
            'production': {
                'errors': prod_metrics.error_count,
                'avg_duration_ms': prod_metrics.avg_duration_ms,
                'invocations': prod_metrics.invocation_count,
                'throttles': prod_metrics.throttle_count
            },
            'shadow': {
                'errors': shadow_metrics.error_count,
                'avg_duration_ms': shadow_metrics.avg_duration_ms,
                'invocations': shadow_metrics.invocation_count,
                'throttles': shadow_metrics.throttle_count
            },
            'delta': {
                'error_rate_increase': (
                    (shadow_metrics.error_count / max(shadow_metrics.invocation_count, 1)) -
                    (prod_metrics.error_count / max(prod_metrics.invocation_count, 1))
                ) * 100,
                'duration_increase_pct': (
                    ((shadow_metrics.avg_duration_ms - prod_metrics.avg_duration_ms) / 
                     max(prod_metrics.avg_duration_ms, 1)) * 100
                )
            }
        }
        
        return comparison

    def should_rollback(self, comparison: Dict, 
                       error_threshold: float = 5.0,
                       duration_threshold_pct: float = 50.0) -> bool:
        """
        Determine if deployment should be rolled back
        
        Args:
            comparison: Metrics comparison dict
            error_threshold: Max acceptable error rate increase (%)
            duration_threshold_pct: Max acceptable duration increase (%)
        """
        delta = comparison['delta']
        
        if delta['error_rate_increase'] > error_threshold:
            logger.warning(f"Error rate increased by {delta['error_rate_increase']:.2f}% (threshold: {error_threshold}%)")
            return True
        
        if delta['duration_increase_pct'] > duration_threshold_pct:
            logger.warning(f"Duration increased by {delta['duration_increase_pct']:.2f}% (threshold: {duration_threshold_pct}%)")
            return True
        
        return False

    def rollback(self, agent: str) -> None:
        """Rollback shadow deployment by removing traffic routing"""
        logger.warning(f"Rolling back deployment for {agent}...")
        
        # Get current production version
        prod_alias = self.get_alias_info(agent, 'production')
        prod_version = prod_alias['FunctionVersion']
        
        # Remove traffic routing (100% to production)
        self.update_alias(agent, 'production', prod_version, routing_config={})
        
        logger.info(f"Rollback complete: 100% traffic to production version {prod_version}")

    def promote_to_production(self, agent: str, shadow_version: str) -> None:
        """Promote shadow version to production"""
        logger.info(f"Promoting shadow version {shadow_version} to production for {agent}...")
        
        # Update production alias to shadow version
        self.update_alias(agent, 'production', shadow_version)
        
        # Update shadow alias to same version (for consistency)
        self.update_alias(agent, 'shadow', shadow_version)
        
        logger.info(f"Promotion complete: production and shadow both on version {shadow_version}")

    def record_deployment_state(self, agent: str, deployment_id: str, 
                               state: str, metadata: Dict) -> None:
        """Record deployment state in DynamoDB"""
        self.state_table.put_item(
            Item={
                'agent_name': agent,
                'deployment_id': deployment_id,
                'status': state,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': json.dumps(metadata)
            }
        )

    def deploy_with_monitoring(self, agent: str, traffic_split: int = 10,
                              monitoring_duration_minutes: int = 15,
                              auto_promote: bool = False) -> bool:
        """
        Execute shadow deployment with automated monitoring
        
        Returns:
            True if deployment succeeded, False if rolled back
        """
        deployment_id = f"{agent}-{int(time.time())}"
        
        try:
            # Step 1: Publish new version
            logger.info(f"=== Starting shadow deployment for {agent} ===")
            new_version = self.publish_new_version(agent)
            
            self.record_deployment_state(agent, deployment_id, 'PUBLISHED', {
                'version': new_version
            })
            
            # Step 2: Update shadow alias
            self.update_alias(agent, 'shadow', new_version)
            
            self.record_deployment_state(agent, deployment_id, 'SHADOW_UPDATED', {
                'version': new_version
            })
            
            # Step 3: Shift traffic
            self.shift_traffic(agent, new_version, traffic_split)
            
            self.record_deployment_state(agent, deployment_id, 'TRAFFIC_SHIFTED', {
                'version': new_version,
                'traffic_split': traffic_split
            })
            
            # Step 4: Monitor metrics
            logger.info(f"Monitoring deployment for {monitoring_duration_minutes} minutes...")
            time.sleep(monitoring_duration_minutes * 60)
            
            comparison = self.compare_metrics(agent, monitoring_duration_minutes)
            logger.info(f"Metrics comparison:\n{json.dumps(comparison, indent=2)}")
            
            # Step 5: Decide: rollback or promote
            if self.should_rollback(comparison):
                self.rollback(agent)
                self.record_deployment_state(agent, deployment_id, 'ROLLED_BACK', {
                    'version': new_version,
                    'reason': 'metrics_threshold_exceeded',
                    'comparison': comparison
                })
                return False
            
            logger.info(f"✅ Shadow deployment successful for {agent}")
            
            if auto_promote:
                self.promote_to_production(agent, new_version)
                self.record_deployment_state(agent, deployment_id, 'PROMOTED', {
                    'version': new_version
                })
                logger.info(f"✅ Promoted version {new_version} to production")
            else:
                self.record_deployment_state(agent, deployment_id, 'MONITORING', {
                    'version': new_version,
                    'awaiting_promotion': True
                })
                logger.info(f"⏸️  Deployment in monitoring state. Run with --promote to promote to production.")
            
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            self.record_deployment_state(agent, deployment_id, 'FAILED', {
                'error': str(e)
            })
            return False


def main():
    parser = argparse.ArgumentParser(description='Shadow Deployment Orchestrator')
    parser.add_argument('--agent', choices=AGENT_LIST + ['all'], 
                       help='Agent to deploy (or "all" for all agents)')
    parser.add_argument('--traffic-split', type=int, default=10,
                       help='Percentage of traffic to route to shadow (default: 10)')
    parser.add_argument('--monitoring-duration', type=int, default=15,
                       help='Monitoring duration in minutes (default: 15)')
    parser.add_argument('--auto-promote', action='store_true',
                       help='Automatically promote to production on success')
    parser.add_argument('--rollback', action='store_true',
                       help='Rollback current deployment')
    parser.add_argument('--promote', action='store_true',
                       help='Promote current shadow to production')
    
    args = parser.parse_args()
    
    orchestrator = ShadowDeploymentOrchestrator()
    
    agents = AGENT_LIST if args.agent == 'all' else [args.agent]
    
    if args.rollback:
        for agent in agents:
            orchestrator.rollback(agent)
        return
    
    if args.promote:
        for agent in agents:
            shadow_info = orchestrator.get_alias_info(agent, 'shadow')
            orchestrator.promote_to_production(agent, shadow_info['FunctionVersion'])
        return
    
    # Execute shadow deployment
    results = {}
    for agent in agents:
        success = orchestrator.deploy_with_monitoring(
            agent=agent,
            traffic_split=args.traffic_split,
            monitoring_duration_minutes=args.monitoring_duration,
            auto_promote=args.auto_promote
        )
        results[agent] = success
    
    # Summary
    logger.info("\n=== Deployment Summary ===")
    for agent, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED/ROLLED BACK"
        logger.info(f"{agent}: {status}")
    
    sys.exit(0 if all(results.values()) else 1)


if __name__ == '__main__':
    main()
