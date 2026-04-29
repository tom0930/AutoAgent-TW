# Task 1: DAG Parser & Dependencies Sorting

**目標**: 
解析 `ConsensusResult` 中的任務依賴，生成拓撲排序的執行隊列。若偵測到循環依賴，則需有安全的 Fallback 機制。

## 具體步驟
1. 建立 `scripts/execution/schemas.py` 定義 `ExecutionNode` Schema。
2. 建立 `scripts/execution/dag.py`。
3. 實作 `build_dag(consensus_result: dict) -> List[ExecutionNode]` 函數。
4. 使用 Python 內建的 `graphlib.TopologicalSorter` 處理相依性。
5. 實作異常捕捉 (`graphlib.CycleError`)，並在遇到時將圖扁平化 (Sequential Fallback)。
6. 撰寫單元測試 `tests/test_execution_dag.py` 驗證其排序與 fallback。

## 驗證標準 (UAT Criteria)
- `python -m pytest tests/test_execution_dag.py -v` 必須通過 (`exit_code == 0`)。
- 測試案例必須涵蓋「無相依性」、「複雜相依性」以及「循環相依性 (Cycle)」。
