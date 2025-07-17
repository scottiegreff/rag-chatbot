# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 11:59:08  
**Test ID:** 2025-07-16_11-59-08  
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
**Test Time:** 2025-07-16T11:58:28.070021

#### Simple Query

- **Total Time:** 16485.2ms
- **First Token Latency:** 14352.2ms
- **Generation Time:** 2133.0ms
- **Tokens Generated:** 11
- **Tokens/Second:** 5.16
- **Response Length:** 110 characters

**Response Preview:**  I do not have access to real-time data, but according to the given material, France's capital city is Paris.


#### Rag Query

- **Total Time:** 5947.0ms
- **First Token Latency:** 2043.4ms
- **Generation Time:** 3903.6ms
- **Tokens Generated:** 16
- **Tokens/Second:** 4.10
- **Response Length:** 199 characters

**Response Preview:**  Coady (Coody) Scott were two of the most famous scientists in FCIA’s history. They worked for decades in FCIA’s labs, conducting groundbreaking research and discoveries that revolutionized the field

#### Sql Query

- **Total Time:** 7528.0ms
- **First Token Latency:** 6342.7ms
- **Generation Time:** 1185.3ms
- **Tokens Generated:** 5
- **Tokens/Second:** 4.22
- **Response Length:** 51 characters

**Response Preview:**  There are 40 products in our e-commercce database.

#### Long Generation

- **Total Time:** 10856.0ms
- **First Token Latency:** 6733.3ms
- **Generation Time:** 4122.7ms
- **Tokens Generated:** 22
- **Tokens/Second:** 5.34
- **Response Length:** 307 characters

**Response Preview:**  Machine Learning is a branch of AI that involves the use of algorithms and data to teach computers to make predictions or decisions based on observed patterns. Some common applications of machine lea...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 4.70 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
