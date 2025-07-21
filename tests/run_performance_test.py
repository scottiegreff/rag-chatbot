#!/usr/bin/env python3
"""
Comprehensive Performance Testing Script for AI Chatbot
Tests M1 GPU vs Docker CPU environments and generates detailed reports.
"""

import subprocess
import time
import json
import requests
import os
import sys
from datetime import datetime
import re
from typing import Dict, List, Tuple

class PerformanceTester:
    def __init__(self):
        # Get port from environment or default to 8000
        port = os.getenv("PORT", "8000")
        self.base_url = f"http://localhost:{port}"
        self.test_results = {}
        self.current_environment = None
        # Always resolve the project root (parent of this script's directory)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.summaries_dir = os.path.join(self.project_root, 'testing_summaries')
        
    def log(self, message: str):
        """Print timestamped log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_command(self, command: str, timeout: int = 120) -> Tuple[bool, str]:
        """Run a shell command and return success status and output"""
        try:
            # Set up environment variables for the subprocess
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Run command without start_new_session to maintain environment
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                env=env,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Run from project root
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, str(e)
            
    def switch_to_local(self) -> bool:
        """Switch to M1 GPU local environment"""
        self.log("🔄 Switching to M1 GPU (Local) environment...")
        success, output = self.run_command("PORT=8000 ./switch-to-local.sh")
        if success:
            self.log("✅ Successfully switched to M1 GPU")
            self.current_environment = "M1 GPU (Local)"
            # Use port 8000 for local environment
            self.base_url = "http://localhost:8000"
            time.sleep(10)  # Wait for backend to start
            return True
        else:
            self.log(f"❌ Failed to switch to M1 GPU: {output}")
            return False
            
    def switch_to_docker(self) -> bool:
        """Switch to Docker CPU environment"""
        self.log("🔄 Switching to Docker CPU environment...")
        success, output = self.run_command("PORT=8000 ./switch-to-docker.sh")
        if success:
            self.log("✅ Successfully switched to Docker CPU")
            self.current_environment = "Docker CPU"
            # Use port 8000 for Docker environment
            self.base_url = "http://localhost:8000"
            time.sleep(15)  # Wait for backend to start
            return True
        else:
            self.log(f"❌ Failed to switch to Docker CPU: {output}")
            return False
            
    def wait_for_backend(self, max_attempts: int = 30) -> bool:
        """Wait for backend to be ready"""
        self.log("⏳ Waiting for backend to be ready...")
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.base_url}/test", timeout=5)
                if response.status_code == 200:
                    self.log("✅ Backend is ready")
                    return True
            except:
                pass
            time.sleep(2)
        self.log("❌ Backend failed to start")
        return False
        
    def send_chat_request(self, message: str, session_id: str) -> Dict:
        """Send a chat request and measure timing"""
        self.log(f"📤 Sending request: {message[:50]}...")
        start_time = time.time()
        
        try:
            self.log(f"🌐 Making POST request to {self.base_url}/api/chat/stream")
            response = requests.post(
                f"{self.base_url}/api/chat/stream",
                json={"message": message, "session_id": session_id},
                timeout=120,
                stream=True
            )
            
            if response.status_code != 200:
                self.log(f"❌ HTTP Error: {response.status_code}")
                return {"error": f"HTTP {response.status_code}", "success": False}
            
            self.log("📥 Starting to read streaming response...")
            # Read the streaming response
            tokens = []
            first_token_time = None
            line_count = 0
            
            for line in response.iter_lines():
                if line:
                    line_count += 1
                    if line_count % 10 == 0:  # Log every 10th line
                        self.log(f"📄 Processing line {line_count}...")
                    
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        if data_str != '{"end": true}':
                            try:
                                data = json.loads(data_str)
                                if 'delta' in data:
                                    tokens.append(data['delta'])
                                    if first_token_time is None:
                                        first_token_time = time.time()
                                        self.log(f"⚡ First token received after {time.time() - start_time:.2f}s")
                            except json.JSONDecodeError:
                                continue
                                
            end_time = time.time()
            
            self.log(f"✅ Request completed in {end_time - start_time:.2f}s")
            self.log(f"📊 Generated {len(tokens)} tokens")
            
            # Calculate metrics
            total_time = (end_time - start_time) * 1000  # Convert to ms
            first_token_latency = (first_token_time - start_time) * 1000 if first_token_time else 0
            generation_time = (end_time - first_token_time) * 1000 if first_token_time else 0
            token_count = len(tokens)
            tokens_per_second = token_count / (generation_time / 1000) if generation_time > 0 else 0
            
            return {
                "success": True,
                "total_time": total_time,
                "first_token_latency": first_token_latency,
                "generation_time": generation_time,
                "token_count": token_count,
                "tokens_per_second": tokens_per_second,
                "response": ''.join(tokens)
            }
            
        except Exception as e:
            self.log(f"❌ Exception occurred: {str(e)}")
            return {"error": str(e), "success": False}
            
    def run_test_suite(self, environment: str) -> Dict:
        """Run a complete test suite for an environment"""
        self.log(f"🧪 Running test suite for {environment}")
        
        test_results = {
            "environment": environment,
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test 1: Simple generic query
        self.log("📝 Test 1: Simple generic query")
        self.log("=" * 50)
        result = self.send_chat_request(
            "What is the capital of France?", 
            f"test-{environment.lower().replace(' ', '-')}-simple"
        )
        test_results["tests"]["simple_query"] = result
        self.log(f"📋 Test 1 result: {'✅ Success' if result.get('success') else '❌ Failed'}")
        self.log("=" * 50)
        
        # Test 2: Complex RAG query
        self.log("📚 Test 2: RAG query with context")
        self.log("=" * 50)
        result = self.send_chat_request(
            "Tell me about Cody and Scott's adventures at FCIAS", 
            f"test-{environment.lower().replace(' ', '-')}-rag"
        )
        test_results["tests"]["rag_query"] = result
        self.log(f"📋 Test 2 result: {'✅ Success' if result.get('success') else '❌ Failed'}")
        self.log("=" * 50)
        
        # Test 3: SQL database query
        self.log("🗄️ Test 3: SQL database query")
        self.log("=" * 50)
        result = self.send_chat_request(
            "How many products do we have in our database?", 
            f"test-{environment.lower().replace(' ', '-')}-sql"
        )
        test_results["tests"]["sql_query"] = result
        self.log(f"📋 Test 3 result: {'✅ Success' if result.get('success') else '❌ Failed'}")
        self.log("=" * 50)
        
        # Test 4: Long generation test
        self.log("📖 Test 4: Long generation test")
        self.log("=" * 50)
        result = self.send_chat_request(
            "Write a detailed explanation of machine learning with examples", 
            f"test-{environment.lower().replace(' ', '-')}-long"
        )
        test_results["tests"]["long_generation"] = result
        self.log(f"📋 Test 4 result: {'✅ Success' if result.get('success') else '❌ Failed'}")
        self.log("=" * 50)
        
        self.log(f"🎉 All tests completed for {environment}")
        return test_results
        
    def generate_markdown_report(self, results: Dict) -> str:
        """Generate a comprehensive markdown report"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        report = f"""# AI Chatbot Performance Test Report

**Test Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Test ID:** {timestamp}  
**Model:** Mistral 7B Instruct v0.2 (Q4_K_M quantization)  
**Hardware:** Apple M1 Mac  

---

## Test Configuration

| **Component** | **M1 GPU (Local)** | **Docker CPU** |
|---------------|-------------------|----------------|
| **Environment** | Native macOS with Metal | Docker container |
| **GPU Layers** | 4 (Metal acceleration) | 4 (containerized) |
| **Memory Access** | Direct Metal API | Virtualized container |

---

## Performance Results

### M1 GPU (Local) Results

"""
        
        # Add M1 GPU results
        if "M1 GPU (Local)" in results:
            m1_results = results["M1 GPU (Local)"]
            report += self._format_environment_results("M1 GPU (Local)", m1_results)
            
        report += "\n### Docker CPU Results\n\n"
        
        # Add Docker CPU results
        if "Docker CPU" in results:
            docker_results = results["Docker CPU"]
            report += self._format_environment_results("Docker CPU", docker_results)
            
        # Add comparison table
        report += self._generate_comparison_table(results)
        
        # Add conclusions
        report += self._generate_conclusions(results)
        
        return report
        
    def _format_environment_results(self, env_name: str, results: Dict) -> str:
        """Format results for a specific environment"""
        report = f"**Environment:** {env_name}\n"
        report += f"**Test Time:** {results['timestamp']}\n\n"
        
        for test_name, test_result in results["tests"].items():
            if test_result.get("success"):
                report += f"#### {test_name.replace('_', ' ').title()}\n\n"
                report += f"- **Total Time:** {test_result['total_time']:.1f}ms\n"
                report += f"- **First Token Latency:** {test_result['first_token_latency']:.1f}ms\n"
                report += f"- **Generation Time:** {test_result['generation_time']:.1f}ms\n"
                report += f"- **Tokens Generated:** {test_result['token_count']}\n"
                report += f"- **Tokens/Second:** {test_result['tokens_per_second']:.2f}\n"
                report += f"- **Response Length:** {len(test_result['response'])} characters\n\n"
                
                # Add response preview
                preview = test_result['response'][:200] + "..." if len(test_result['response']) > 200 else test_result['response']
                report += f"**Response Preview:** {preview}\n\n"
            else:
                report += f"#### {test_name.replace('_', ' ').title()}\n\n"
                report += f"❌ **Error:** {test_result.get('error', 'Unknown error')}\n\n"
                
        return report
        
    def _generate_comparison_table(self, results: Dict) -> str:
        """Generate comparison table between environments"""
        report = "## Performance Comparison\n\n"
        report += "| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |\n"
        report += "|---------------|------------|------------|----------------|---------------------|\n"
        
        test_types = ["simple_query", "rag_query", "sql_query", "long_generation"]
        
        for test_type in test_types:
            m1_result = results.get("M1 GPU (Local)", {}).get("tests", {}).get(test_type, {})
            docker_result = results.get("Docker CPU", {}).get("tests", {}).get(test_type, {})
            
            if m1_result.get("success") and docker_result.get("success"):
                # First token latency comparison
                m1_latency = m1_result.get("first_token_latency", 0)
                docker_latency = docker_result.get("first_token_latency", 0)
                if docker_latency > 0:
                    ratio = docker_latency / m1_latency
                    report += f"| {test_type.replace('_', ' ').title()} | First Token Latency | {m1_latency:.1f}ms | {docker_latency:.1f}ms | **{ratio:.1f}x faster** |\n"
                
                # Token generation speed comparison
                m1_speed = m1_result.get("tokens_per_second", 0)
                docker_speed = docker_result.get("tokens_per_second", 0)
                if docker_speed > 0:
                    ratio = m1_speed / docker_speed
                    report += f"| {test_type.replace('_', ' ').title()} | Token Generation Speed | {m1_speed:.2f} tokens/sec | {docker_speed:.2f} tokens/sec | **{ratio:.1f}x faster** |\n"
                    
        return report
        
    def _generate_conclusions(self, results: Dict) -> str:
        """Generate conclusions based on test results"""
        report = "## Key Findings\n\n"
        
        # Calculate average improvements
        improvements = []
        for env_name, env_results in results.items():
            for test_name, test_result in env_results.get("tests", {}).items():
                if test_result.get("success"):
                    improvements.append({
                        "test": test_name,
                        "environment": env_name,
                        "tokens_per_second": test_result.get("tokens_per_second", 0),
                        "first_token_latency": test_result.get("first_token_latency", 0)
                    })
        
        # Check if we have results from both environments
        m1_results = [i for i in improvements if i["environment"] == "M1 GPU (Local)"]
        docker_results = [i for i in improvements if i["environment"] == "Docker CPU"]
        
        if len(m1_results) > 0 and len(docker_results) > 0:
            m1_avg_speed = sum([i["tokens_per_second"] for i in m1_results]) / len(m1_results)
            docker_avg_speed = sum([i["tokens_per_second"] for i in docker_results]) / len(docker_results)
            
            if docker_avg_speed > 0:
                speed_ratio = m1_avg_speed / docker_avg_speed
                report += f"- **Average Token Generation:** M1 GPU is **{speed_ratio:.1f}x faster** ({m1_avg_speed:.2f} vs {docker_avg_speed:.2f} tokens/sec)\n"
        elif len(docker_results) > 0:
            docker_avg_speed = sum([i["tokens_per_second"] for i in docker_results]) / len(docker_results)
            report += f"- **Docker CPU Performance:** Average {docker_avg_speed:.2f} tokens/sec\n"
            report += f"- **M1 GPU Results:** Not available (environment switch failed)\n"
        elif len(m1_results) > 0:
            m1_avg_speed = sum([i["tokens_per_second"] for i in m1_results]) / len(m1_results)
            report += f"- **M1 GPU Performance:** Average {m1_avg_speed:.2f} tokens/sec\n"
            report += f"- **Docker CPU Results:** Not available\n"
        else:
            report += f"- **No successful test results available**\n"
        
        report += "\n## Recommendations\n\n"
        report += "- **For Production:** Use M1 GPU with Metal acceleration for optimal performance\n"
        report += "- **For Development:** Docker CPU provides consistent cross-platform compatibility\n"
        report += "- **For Testing:** Use this script for ongoing performance monitoring\n"
        
        return report
        
    def run_comprehensive_test(self):
        """Run the complete comprehensive test"""
        self.log("🚀 Starting comprehensive performance test...")
        
        # Set environment variables for faster testing
        os.environ['MAX_NEW_TOKENS'] = '50'  # Limit tokens for faster testing
        self.log("⚙️ Set MAX_NEW_TOKENS=50 for faster testing")
        
        # Always create summaries in the project root
        os.makedirs(self.summaries_dir, exist_ok=True)
        
        # Test M1 GPU
        self.log("🔄 Phase 1: Testing M1 GPU environment...")
        if self.switch_to_local() and self.wait_for_backend():
            self.log("✅ M1 GPU environment ready, starting tests...")
            m1_results = self.run_test_suite("M1 GPU (Local)")
            self.test_results["M1 GPU (Local)"] = m1_results
            self.log("✅ M1 GPU tests completed")
        else:
            self.log("❌ Failed to test M1 GPU environment")
            
        # Test Docker CPU
        self.log("🔄 Phase 2: Testing Docker CPU environment...")
        if self.switch_to_docker() and self.wait_for_backend():
            self.log("✅ Docker CPU environment ready, starting tests...")
            docker_results = self.run_test_suite("Docker CPU")
            self.test_results["Docker CPU"] = docker_results
            self.log("✅ Docker CPU tests completed")
        else:
            self.log("❌ Failed to test Docker CPU environment")
            
        # Generate report
        self.log("📝 Generating comprehensive report...")
        report = self.generate_markdown_report(self.test_results)
        
        # Save report in the project root summaries dir
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.summaries_dir, f"performance_test_{timestamp}.md")
        
        with open(filename, 'w') as f:
            f.write(report)
            
        self.log(f"✅ Report saved to: {filename}")
        self.log("🎉 Comprehensive performance test completed!")
        
        return filename

def main():
    """Main function"""
    print("🤖 AI Chatbot Performance Testing Suite")
    print("=" * 50)
    
    tester = PerformanceTester()
    report_file = tester.run_comprehensive_test()
    
    print(f"\n📊 Test completed! Report saved to: {report_file}")
    print("📖 You can view the report in your markdown viewer or browser.")

if __name__ == "__main__":
    main() 