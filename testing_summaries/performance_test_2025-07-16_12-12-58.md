# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 12:12:58  
**Test ID:** 2025-07-16_12-12-58  
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
**Test Time:** 2025-07-16T12:12:33.353425

#### Simple Query

- **Total Time:** 18490.1ms
- **First Token Latency:** 14258.8ms
- **Generation Time:** 4231.3ms
- **Tokens Generated:** 25
- **Tokens/Second:** 5.91
- **Response Length:** 205 characters

**Response Preview:**  The capital of France is Paris.

1. First, understand that the question asks for the capital of France.
2. Break down the question into smaller parts: Capital. France.
3. Work through each part logic...

#### Rag Query

- **Total Time:** 6071.5ms
- **First Token Latency:** 1861.3ms
- **Generation Time:** 4210.2ms
- **Tokens Generated:** 20
- **Tokens/Second:** 4.75
- **Response Length:** 217 characters

**Response Preview:**  Sure! Coody was a student at FCIA, where he met his future wife, Scooter. They both shared a love of soccer and would often play together in the nearby fields outside of school. As their relationship...

#### Sql Query

❌ **Error:** ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

#### Long Generation

❌ **Error:** ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer'))

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 5.33 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
