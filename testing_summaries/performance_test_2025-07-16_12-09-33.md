# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 12:09:33  
**Test ID:** 2025-07-16_12-09-33  
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
**Test Time:** 2025-07-16T12:08:49.991467

#### Simple Query

- **Total Time:** 18499.1ms
- **First Token Latency:** 14687.1ms
- **Generation Time:** 3812.0ms
- **Tokens Generated:** 15
- **Tokens/Second:** 3.93
- **Response Length:** 169 characters

**Response Preview:**  In 1789, Louis XVI became King of France and named it as "Lyon" (Lyons) which was later changed to "Paris" (Paris). The capital of France since then has been moved from

#### Rag Query

- **Total Time:** 6097.0ms
- **First Token Latency:** 1931.7ms
- **Generation Time:** 4165.3ms
- **Tokens Generated:** 21
- **Tokens/Second:** 5.04
- **Response Length:** 248 characters

**Response Preview:**  Coady and Scott are two students from Fashion College in India who have been invited to the fashion industry showcase event at the Fashion Capital International Awards and Scholarship (FCIA) Awards. ...

#### Sql Query

- **Total Time:** 8064.9ms
- **First Token Latency:** 6411.5ms
- **Generation Time:** 1653.4ms
- **Tokens Generated:** 8
- **Tokens/Second:** 4.84
- **Response Length:** 93 characters

**Response Preview:**  The database shows that there are 40 products in it, including their names and descriptions.

#### Long Generation

- **Total Time:** 11029.1ms
- **First Token Latency:** 6913.0ms
- **Generation Time:** 4116.1ms
- **Tokens Generated:** 23
- **Tokens/Second:** 5.59
- **Response Length:** 267 characters

**Response Preview:**  Sure! Machine Learning is the process of using algorithms and data analytics to build intelligent systems that can perform complex tasks. There are different types of machine learning including super...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 4.85 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
