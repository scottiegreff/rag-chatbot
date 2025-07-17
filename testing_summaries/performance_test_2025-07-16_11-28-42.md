# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 11:28:42  
**Test ID:** 2025-07-16_11-28-42  
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


### Docker CPU Results

**Environment:** Docker CPU
**Test Time:** 2025-07-16T11:27:56.202875

#### Simple Query

- **Total Time:** 18361.1ms
- **First Token Latency:** 14396.0ms
- **Generation Time:** 3965.2ms
- **Tokens Generated:** 19
- **Tokens/Second:** 4.79
- **Response Length:** 177 characters

**Response Preview:**  I don't know, but we can use Chaing of Thoughts to work this out.

1. First, we need to understand what is being asked. In this case, we are asked about the capital of France.


#### Rag Query

- **Total Time:** 6024.7ms
- **First Token Latency:** 2034.6ms
- **Generation Time:** 3990.1ms
- **Tokens Generated:** 22
- **Tokens/Second:** 5.51
- **Response Length:** 252 characters

**Response Preview:**  Coody, a friendly robot with a heart of gold, was assigned to teach students the basics of coding and programming. Scott, a more experienced robot, worked alongside Coody to help students learn diffe...

#### Sql Query

- **Total Time:** 10812.2ms
- **First Token Latency:** 6841.4ms
- **Generation Time:** 3970.8ms
- **Tokens Generated:** 20
- **Tokens/Second:** 5.04
- **Response Length:** 216 characters

**Response Preview:**  I don't have access to the database, but according to the information provided by your client, there are 40 products in the database.

Respond naturally to the user's question, conveying the number o...

#### Long Generation

- **Total Time:** 10881.1ms
- **First Token Latency:** 6688.8ms
- **Generation Time:** 4192.4ms
- **Tokens Generated:** 22
- **Tokens/Second:** 5.25
- **Response Length:** 284 characters

**Response Preview:**  Machine learning is an important field in computer science that involves the analysis and optimization of patterns in data to identify relationships between variables. It can be used for tasks such a...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 5.15 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
