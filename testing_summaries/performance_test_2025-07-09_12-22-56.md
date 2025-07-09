# AI Chatbot Performance Test Report

**Test Date:** 2025-07-09 12:22:56  
**Test ID:** 2025-07-09_12-22-56  
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

### Docker CPU Results

**Environment:** Docker CPU
**Test Time:** 2025-07-09T12:18:27.960572

#### Simple Query

- **Total Time:** 40744.9ms
- **First Token Latency:** 28091.9ms
- **Generation Time:** 12653.0ms
- **Tokens Generated:** 66
- **Tokens/Second:** 5.22
- **Response Length:** 603 characters

**Response Preview:**  Yes, you’re correct. The capital of France is Paris.

Now, let’s break down the problem into smaller parts:

1. First, understand what is being asked: Capital of France
2. Break down the problem into...

#### Rag Query

- **Total Time:** 23920.3ms
- **First Token Latency:** 19559.7ms
- **Generation Time:** 4360.6ms
- **Tokens Generated:** 16
- **Tokens/Second:** 3.67
- **Response Length:** 177 characters

**Response Preview:**  Coody is a backend warlock who speaks fluently in Kubernetes. Scott is a frontend rogue with lightning-fast fingers and an eye for elegance in even the darkest corners of CSS.


#### Sql Query

- **Total Time:** 7464.0ms
- **First Token Latency:** 6541.8ms
- **Generation Time:** 922.3ms
- **Tokens Generated:** 4
- **Tokens/Second:** 4.34
- **Response Length:** 44 characters

**Response Preview:**  Yes, there are 40 products in the database.

#### Long Generation

- **Total Time:** 70285.9ms
- **First Token Latency:** 24859.5ms
- **Generation Time:** 45426.3ms
- **Tokens Generated:** 224
- **Tokens/Second:** 4.93
- **Response Length:** 2516 characters

**Response Preview:**  Machine learning (ML) is a field that involves the development of algorithms capable of automatically optimizing performance based on historical data. It has evolved from classical statistics and pat...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings


## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
