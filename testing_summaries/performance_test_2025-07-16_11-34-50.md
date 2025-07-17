# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 11:34:50  
**Test ID:** 2025-07-16_11-34-50  
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
**Test Time:** 2025-07-16T11:34:06.904420

#### Simple Query

- **Total Time:** 17938.7ms
- **First Token Latency:** 13847.4ms
- **Generation Time:** 4091.3ms
- **Tokens Generated:** 23
- **Tokens/Second:** 5.62
- **Response Length:** 203 characters

**Response Preview:**  France is not a country, but a region in Europe with a large population. The capital of France is Paris, which has a population of over 12 million people.

Break down the problem into smaller parts:
...

#### Rag Query

- **Total Time:** 6331.6ms
- **First Token Latency:** 1688.8ms
- **Generation Time:** 4642.8ms
- **Tokens Generated:** 20
- **Tokens/Second:** 4.31
- **Response Length:** 205 characters

**Response Preview:**  Sure! Coody and Scott are two famous FCIA students who have been attending FCIA since 2015. They were initially interested in the program due to its reputation for producing top-notch engineers. Cood...

#### Sql Query

- **Total Time:** 8891.2ms
- **First Token Latency:** 6598.8ms
- **Generation Time:** 2292.4ms
- **Tokens Generated:** 12
- **Tokens/Second:** 5.23
- **Response Length:** 138 characters

**Response Preview:**  I don't have access to your database. However, according to the information available, there are 40 products in your e-commerce database.

#### Long Generation

- **Total Time:** 10679.6ms
- **First Token Latency:** 6536.9ms
- **Generation Time:** 4142.7ms
- **Tokens Generated:** 21
- **Tokens/Second:** 5.07
- **Response Length:** 223 characters

**Response Preview:**  Sure! Machine Learning is a field that deals with the development and application of algorithms to solve complex problems. It involves two main concepts: data mining and model building. Here's an ove...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 5.06 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
