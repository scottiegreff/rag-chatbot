# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 12:59:59  
**Test ID:** 2025-07-16_12-59-59  
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
**Test Time:** 2025-07-16T12:59:56.526621

#### Simple Query

- **Total Time:** 1219.6ms
- **First Token Latency:** 727.3ms
- **Generation Time:** 492.3ms
- **Tokens Generated:** 16
- **Tokens/Second:** 32.50
- **Response Length:** 166 characters

**Response Preview:**  I don't have access to real-time data, but here's what I can tell you: France has two capitals - Paris and Strasbourg. Paris is known as the capital city of France.


#### Rag Query

- **Total Time:** 827.3ms
- **First Token Latency:** 298.8ms
- **Generation Time:** 528.5ms
- **Tokens Generated:** 23
- **Tokens/Second:** 43.52
- **Response Length:** 301 characters

**Response Preview:**  Coady was a brilliant engineer who joined the Federation of International Associations for Science after he graduated from the University of California with a degree in mechanical engineering. He qui...

#### Sql Query

- **Total Time:** 499.3ms
- **First Token Latency:** 352.8ms
- **Generation Time:** 146.5ms
- **Tokens Generated:** 5
- **Tokens/Second:** 34.13
- **Response Length:** 61 characters

**Response Preview:**  Based on the results, there are 40 products in the database.

#### Long Generation

- **Total Time:** 857.9ms
- **First Token Latency:** 311.7ms
- **Generation Time:** 546.3ms
- **Tokens Generated:** 22
- **Tokens/Second:** 40.27
- **Response Length:** 254 characters

**Response Preview:**  Machine Learning is a branch of Artificial Intelligence that involves the use of algorithms to improve and automate various tasks in the real world. One example of machine learning is the development...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 37.61 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
