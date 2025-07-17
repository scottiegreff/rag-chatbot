# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 11:05:58  
**Test ID:** 2025-07-16_11-05-58  
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
**Test Time:** 2025-07-16T11:05:15.335826

#### Simple Query

- **Total Time:** 18237.3ms
- **First Token Latency:** 14074.2ms
- **Generation Time:** 4163.2ms
- **Tokens Generated:** 22
- **Tokens/Second:** 5.28
- **Response Length:** 198 characters

**Response Preview:**  The capital of France is Paris.

First, we need to know what question we are answering. In this case, it's "What is the capital of France?"

Second, we break down the problem into smaller parts. We

#### Rag Query

- **Total Time:** 5936.9ms
- **First Token Latency:** 2025.4ms
- **Generation Time:** 3911.5ms
- **Tokens Generated:** 18
- **Tokens/Second:** 4.60
- **Response Length:** 208 characters

**Response Preview:**  Sure, I'll tell you! Coody and Scott were the two students who got accepted into FCIA's prestigious Design Innovation Program. The program was designed to nurture their innovative ideas and encourage...

#### Sql Query

- **Total Time:** 8285.8ms
- **First Token Latency:** 6471.8ms
- **Generation Time:** 1814.0ms
- **Tokens Generated:** 8
- **Tokens/Second:** 4.41
- **Response Length:** 99 characters

**Response Preview:**  I do not have access to your e-commerce database. However, there are 40 products in your database.

#### Long Generation

- **Total Time:** 10642.9ms
- **First Token Latency:** 6536.4ms
- **Generation Time:** 4106.5ms
- **Tokens Generated:** 23
- **Tokens/Second:** 5.60
- **Response Length:** 268 characters

**Response Preview:**  Machine learning is the field that focuses on improving the accuracy and efficiency of algorithms to make predictions or decision-making based on data. Here are some common examples of machine learni...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 4.97 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
