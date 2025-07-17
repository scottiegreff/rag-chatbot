# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 12:05:09  
**Test ID:** 2025-07-16_12-05-09  
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
**Test Time:** 2025-07-16T12:04:28.803953

#### Simple Query

- **Total Time:** 15658.7ms
- **First Token Latency:** 14532.1ms
- **Generation Time:** 1126.6ms
- **Tokens Generated:** 8
- **Tokens/Second:** 7.10
- **Response Length:** 70 characters

**Response Preview:**  I don't know the capital of France. Please provide more information.


#### Rag Query

- **Total Time:** 6118.9ms
- **First Token Latency:** 2009.0ms
- **Generation Time:** 4109.9ms
- **Tokens Generated:** 17
- **Tokens/Second:** 4.14
- **Response Length:** 203 characters

**Response Preview:**  They were part of a group of five individuals who were selected to attend the 2019 Festival of Creative Industries and Arts for Students (FCIA) in Adelaide. The festival is an initiative of FCIA and ...

#### Sql Query

- **Total Time:** 7793.7ms
- **First Token Latency:** 6417.1ms
- **Generation Time:** 1376.6ms
- **Tokens Generated:** 6
- **Tokens/Second:** 4.36
- **Response Length:** 73 characters

**Response Preview:**  Based on the results, there are 40 products in your e-commerce database.

#### Long Generation

- **Total Time:** 10792.1ms
- **First Token Latency:** 6756.1ms
- **Generation Time:** 4036.1ms
- **Tokens Generated:** 23
- **Tokens/Second:** 5.70
- **Response Length:** 308 characters

**Response Preview:**  Machine Learning is the study and development of algorithms to improve the accuracy and efficiency of computer systems in identifying patterns, features, and relationships within data sets. Examples ...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 5.32 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
