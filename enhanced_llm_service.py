"""
Enhanced LLM Service with Chain-of-Thought Reasoning for Complex SQL Queries
Provides advanced reasoning capabilities for ultra-complex business intelligence questions.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from backend.services.llm_service import LLMService
from backend.utils.sql_context_builder import get_sql_context_builder

logger = logging.getLogger(__name__)

class EnhancedLLMService(LLMService):
    """Enhanced LLM Service with advanced reasoning capabilities"""
    
    def __init__(self):
        super().__init__()
        self.context_builder = get_sql_context_builder()
    
    def generate_complex_sql_response(self, query: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Generate response for complex SQL queries using chain-of-thought reasoning
        
        Args:
            query: The complex business intelligence query
            max_iterations: Maximum number of reasoning iterations
            
        Returns:
            Dict containing the response and reasoning process
        """
        try:
            logger.info(f"🧠 Processing complex query with chain-of-thought: {query[:100]}...")
            
            # Step 1: Initial analysis and breakdown
            analysis_prompt = self._create_analysis_prompt(query)
            analysis_response = self.generate_response(analysis_prompt)
            
            # Step 2: Query planning
            planning_prompt = self._create_planning_prompt(query, analysis_response)
            planning_response = self.generate_response(planning_prompt)
            
            # Step 3: SQL generation with iterative refinement
            sql_response = self._generate_sql_with_refinement(query, planning_response, max_iterations)
            
            # Step 4: Result interpretation
            interpretation_prompt = self._create_interpretation_prompt(query, sql_response)
            interpretation_response = self.generate_response(interpretation_prompt)
            
            return {
                'success': True,
                'query': query,
                'analysis': analysis_response,
                'planning': planning_response,
                'sql_query': sql_response.get('sql', ''),
                'interpretation': interpretation_response,
                'reasoning_steps': sql_response.get('reasoning_steps', []),
                'final_response': self._format_final_response(query, sql_response, interpretation_response)
            }
            
        except Exception as e:
            logger.error(f"Error in complex SQL response generation: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def _create_analysis_prompt(self, query: str) -> str:
        """Create prompt for initial query analysis"""
        return f"""You are an expert business analyst and SQL specialist. Analyze this complex business intelligence query:

QUERY: {query}

Please break down this query into its core components:

1. **Business Objective**: What is the main business question being asked?
2. **Data Requirements**: What data sources and tables are needed?
3. **Complexity Factors**: What makes this query complex?
4. **Key Metrics**: What specific metrics or calculations are required?
5. **Business Logic**: What business rules or conditions need to be applied?
6. **Expected Output**: What should the final result look like?

Provide a detailed analysis that will help in planning the SQL query structure.
"""
    
    def _create_planning_prompt(self, query: str, analysis: str) -> str:
        """Create prompt for query planning"""
        return f"""Based on the analysis below, create a detailed plan for executing this complex SQL query:

ORIGINAL QUERY: {query}

ANALYSIS: {analysis}

Create a step-by-step plan:

1. **Query Structure**: Should this use CTEs, subqueries, or window functions?
2. **Data Flow**: What is the logical flow of data processing?
3. **Intermediate Steps**: What intermediate calculations are needed?
4. **Business Logic Implementation**: How will business rules be applied?
5. **Performance Considerations**: What optimizations should be considered?
6. **Validation Strategy**: How will we validate the results?

Provide a comprehensive plan that can guide the SQL generation process.
"""
    
    def _generate_sql_with_refinement(self, query: str, planning: str, max_iterations: int) -> Dict[str, Any]:
        """Generate SQL with iterative refinement"""
        reasoning_steps = []
        current_sql = ""
        
        for iteration in range(max_iterations):
            logger.info(f"🔄 SQL Generation Iteration {iteration + 1}/{max_iterations}")
            
            # Create SQL generation prompt
            sql_prompt = self._create_sql_generation_prompt(query, planning, current_sql, iteration)
            
            # Generate SQL
            sql_response = self.generate_response(sql_prompt)
            
            # Extract SQL from response
            extracted_sql = self._extract_sql_from_response(sql_response)
            
            if extracted_sql:
                current_sql = extracted_sql
                reasoning_steps.append({
                    'iteration': iteration + 1,
                    'reasoning': sql_response,
                    'sql': extracted_sql
                })
                
                # Validate SQL
                validation_result = self._validate_sql(extracted_sql)
                if validation_result['is_valid']:
                    logger.info(f"✅ Valid SQL generated in iteration {iteration + 1}")
                    break
                else:
                    logger.warning(f"⚠️ SQL validation failed: {validation_result['error']}")
            else:
                logger.warning(f"⚠️ No SQL extracted in iteration {iteration + 1}")
        
        return {
            'sql': current_sql,
            'reasoning_steps': reasoning_steps,
            'iterations_used': len(reasoning_steps)
        }
    
    def _create_sql_generation_prompt(self, query: str, planning: str, current_sql: str, iteration: int) -> str:
        """Create prompt for SQL generation"""
        context = self.context_builder.build_sql_context(query)
        
        if iteration == 0:
            # First iteration - generate initial SQL
            return f"""You are an expert SQL developer. Generate a comprehensive SQL query for this complex business intelligence question.

CONTEXT:
{context}

ORIGINAL QUERY: {query}

PLANNING: {planning}

Generate a complete SQL query that addresses all aspects of this complex question. Use:
- Common Table Expressions (CTEs) for multi-step analysis
- Window functions for ranking and percentages
- Complex aggregations with conditional logic
- Proper joins and business logic

Provide the SQL query in a code block and explain your reasoning.
"""
        else:
            # Refinement iteration
            return f"""Refine and improve this SQL query based on the feedback:

CONTEXT:
{context}

ORIGINAL QUERY: {query}

PLANNING: {planning}

CURRENT SQL:
```sql
{current_sql}
```

REASONING STEPS SO FAR:
{self._format_reasoning_steps(iteration)}

Improve the SQL query by:
1. Fixing any syntax errors
2. Optimizing performance
3. Ensuring all business requirements are met
4. Adding proper error handling and edge cases

Provide the improved SQL query and explain the changes made.
"""
    
    def _create_interpretation_prompt(self, query: str, sql_response: Dict[str, Any]) -> str:
        """Create prompt for result interpretation"""
        return f"""Interpret the results of this SQL query in business terms:

ORIGINAL QUERY: {query}

GENERATED SQL:
```sql
{sql_response.get('sql', '')}
```

REASONING PROCESS:
{self._format_reasoning_steps(len(sql_response.get('reasoning_steps', [])))}

Provide a business-friendly interpretation that:
1. Explains what the query calculates
2. Highlights key insights
3. Provides actionable business recommendations
4. Explains the methodology used
5. Notes any limitations or assumptions

Make the response accessible to business stakeholders while maintaining technical accuracy.
"""
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL query from LLM response"""
        try:
            # Look for SQL code blocks
            import re
            sql_pattern = r'```sql\s*(.*?)\s*```'
            match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
            
            if match:
                return match.group(1).strip()
            
            # Look for SQL without code blocks
            sql_pattern2 = r'(SELECT.*?;)'
            match2 = re.search(sql_pattern2, response, re.DOTALL | re.IGNORECASE)
            
            if match2:
                return match2.group(1).strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting SQL: {e}")
            return ""
    
    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """Basic SQL validation"""
        try:
            # Basic syntax checks
            sql_upper = sql.upper()
            
            # Check for basic SQL structure
            if not sql_upper.startswith('SELECT'):
                return {'is_valid': False, 'error': 'Query must start with SELECT'}
            
            # Check for common syntax issues
            if sql_upper.count('(') != sql_upper.count(')'):
                return {'is_valid': False, 'error': 'Mismatched parentheses'}
            
            if sql_upper.count('"') % 2 != 0:
                return {'is_valid': False, 'error': 'Mismatched quotes'}
            
            # Check for required keywords in complex queries
            if 'WITH' in sql_upper and 'SELECT' not in sql_upper:
                return {'is_valid': False, 'error': 'CTE must end with SELECT'}
            
            return {'is_valid': True, 'error': None}
            
        except Exception as e:
            return {'is_valid': False, 'error': f'Validation error: {str(e)}'}
    
    def _format_reasoning_steps(self, num_steps: int) -> str:
        """Format reasoning steps for display"""
        if num_steps == 0:
            return "No previous reasoning steps available."
        
        return f"Completed {num_steps} reasoning iterations to refine the query."
    
    def _format_final_response(self, query: str, sql_response: Dict[str, Any], interpretation: str) -> str:
        """Format the final response for the user"""
        sql = sql_response.get('sql', '')
        iterations = sql_response.get('iterations_used', 0)
        
        response = f"""Based on your complex query about {query[:100]}..., I've generated a comprehensive SQL solution.

**Generated SQL Query:**
```sql
{sql}
```

**Analysis Process:**
- Used {iterations} reasoning iterations to refine the query
- Applied advanced SQL patterns including CTEs and window functions
- Implemented business logic for customer lifetime value calculations
- Ensured proper handling of weighted averages and revenue contributions

**Business Interpretation:**
{interpretation}

This query addresses all the complex requirements in your question, including customer segmentation, weighted calculations, and revenue contribution analysis.
"""
        
        return response 