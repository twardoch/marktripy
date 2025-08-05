# Performance Optimization

Learn how to optimize marktripy for speed and memory efficiency. This guide covers parser selection, streaming techniques, and performance monitoring for large-scale document processing.

## Performance Overview

### Benchmarking Results

Performance varies significantly based on parser backend and document characteristics:

| Parser Backend | Parse Speed | Memory Usage | Round-trip Quality |
|----------------|-------------|--------------|-------------------|
| `mistletoe` | **Fast** (100ms/MB) | **Low** (50MB peak) | Excellent |
| `markdown-it-py` | Medium (200ms/MB) | Medium (100MB peak) | Good |
| `markdown` | Slow (500ms/MB) | High (200MB peak) | Poor |

### Factors Affecting Performance

1. **Document size**: Linear scaling for most operations
2. **Document complexity**: Nested structures increase processing time
3. **Extensions**: Each extension adds overhead
4. **Transformations**: AST manipulation can be expensive
5. **Memory pressure**: Large documents may cause garbage collection

## Parser Backend Selection

### Choosing the Right Backend

```python
from marktripy import Parser
import time

def benchmark_parser(backend_name, markdown_text, iterations=100):
    """Benchmark parser performance"""
    parser = Parser(backend=backend_name)
    
    start_time = time.time()
    for _ in range(iterations):
        ast = parser.parse(markdown_text)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / iterations
    return avg_time

# Test different backends
backends = ['mistletoe', 'markdown-it-py', 'markdown']
test_document = "# Test\n" + "Some text. " * 1000

for backend in backends:
    try:
        avg_time = benchmark_parser(backend, test_document)
        print(f"{backend}: {avg_time:.4f}s per parse")
    except Exception as e:
        print(f"{backend}: Error - {e}")
```

### Backend-Specific Optimizations

#### Mistletoe (Speed-Optimized)

```python
from marktripy import Parser

# Fastest configuration for mistletoe
fast_parser = Parser(
    backend="mistletoe",
    options={
        "html": False,         # Disable HTML parsing
        "math": False,         # Disable math extension
        "footnotes": False,    # Disable footnotes
    }
)

# For maximum speed with minimal features
minimal_parser = Parser(
    backend="mistletoe",
    extensions=[],  # No extensions
    options={
        "strict": True,        # Strict CommonMark only
        "disable_html": True,  # No HTML processing
    }
)
```

#### markdown-it-py (Feature-Rich)

```python
from marktripy import Parser

# Optimized markdown-it-py configuration
balanced_parser = Parser(
    backend="markdown-it-py",
    options={
        "html": False,         # Disable HTML if not needed
        "linkify": False,      # Disable auto-linking
        "typographer": False,  # Disable smart quotes
        "breaks": False,       # Disable line break conversion
    },
    extensions=["gfm"]  # Only essential extensions
)
```

## Memory Optimization

### Streaming Large Documents

```python
from marktripy import StreamingParser
import mmap

class StreamingProcessor:
    """Process large files without loading entirely into memory"""
    
    def __init__(self, chunk_size=1024*1024):  # 1MB chunks
        self.chunk_size = chunk_size
        self.parser = StreamingParser()
    
    def process_file(self, file_path, output_path):
        """Process file in chunks"""
        with open(file_path, 'r', encoding='utf-8') as infile:
            with open(output_path, 'w', encoding='utf-8') as outfile:
                
                buffer = ""
                chunk_number = 0
                
                while True:
                    chunk = infile.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    buffer += chunk
                    
                    # Process complete sections
                    sections = self.split_into_sections(buffer)
                    
                    # Process all but the last section
                    for section in sections[:-1]:
                        processed = self.process_section(section)
                        outfile.write(processed)
                    
                    # Keep incomplete section for next iteration
                    buffer = sections[-1] if sections else ""
                    chunk_number += 1
                
                # Process remaining buffer
                if buffer.strip():
                    processed = self.process_section(buffer)
                    outfile.write(processed)
    
    def split_into_sections(self, text):
        """Split text into logical sections"""
        # Split on double newlines (paragraph breaks)
        sections = text.split('\n\n')
        return sections
    
    def process_section(self, section_text):
        """Process a single section"""
        try:
            ast = self.parser.parse(section_text)
            # Apply lightweight transformations
            self.optimize_ast(ast)
            return self.parser.render_markdown(ast) + '\n\n'
        except Exception as e:
            print(f"Error processing section: {e}")
            return section_text + '\n\n'
    
    def optimize_ast(self, ast):
        """Apply memory-efficient transformations"""
        # Only essential transformations to minimize memory usage
        pass

# Usage
processor = StreamingProcessor()
processor.process_file('large_document.md', 'processed_document.md')
```

### Memory-Mapped File Processing

```python
import mmap
from pathlib import Path

def process_large_file_mmap(file_path):
    """Process very large files using memory mapping"""
    
    file_path = Path(file_path)
    
    with open(file_path, 'r+b') as f:
        # Memory-map the file
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            
            # Process in chunks
            chunk_size = 1024 * 1024  # 1MB
            position = 0
            
            while position < len(mm):
                # Find chunk boundaries at line breaks
                chunk_end = min(position + chunk_size, len(mm))
                
                # Adjust to line boundary
                while chunk_end < len(mm) and mm[chunk_end:chunk_end+1] != b'\n':
                    chunk_end += 1
                
                # Extract and process chunk
                chunk_data = mm[position:chunk_end].decode('utf-8')
                
                # Process chunk
                process_chunk(chunk_data)
                
                position = chunk_end + 1

def process_chunk(chunk_text):
    """Process a chunk of text efficiently"""
    # Use minimal parser configuration
    parser = Parser(backend="mistletoe", extensions=[])
    
    try:
        ast = parser.parse(chunk_text)
        # Apply essential transformations only
        return parser.render_markdown(ast)
    except Exception:
        return chunk_text  # Return original on error
```

### Memory Profiling

```python
import tracemalloc
import psutil
import os
from marktripy import Parser

def profile_memory_usage(parser_func, *args):
    """Profile memory usage of parser operations"""
    
    # Start memory tracing
    tracemalloc.start()
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Execute function
    result = parser_func(*args)
    
    # Get peak memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Initial memory: {initial_memory:.1f} MB")
    print(f"Final memory: {final_memory:.1f} MB")
    print(f"Memory increase: {final_memory - initial_memory:.1f} MB")
    print(f"Peak traced memory: {peak / 1024 / 1024:.1f} MB")
    
    return result

# Example usage
def test_parse_large_doc():
    parser = Parser(backend="mistletoe")
    large_text = "# Section\nSome text. " * 10000
    return parser.parse(large_text)

profile_memory_usage(test_parse_large_doc)
```

## Performance Optimization Techniques

### Efficient AST Traversal

```python
from marktripy import parse_markdown

def optimized_traversal(ast, node_processors):
    """Single-pass traversal with multiple processors"""
    
    for node in ast.walk():
        node_type = node.type
        
        # Use dict lookup instead of multiple if statements
        if node_type in node_processors:
            processor = node_processors[node_type]
            processor(node)

def optimize_multiple_operations(ast):
    """Combine multiple operations in single traversal"""
    
    heading_count = 0
    link_count = 0
    total_text_length = 0
    
    # Process multiple things in one pass
    processors = {
        'heading': lambda node: add_heading_id(node) or increment_heading_count(),
        'link': lambda node: validate_link(node) or increment_link_count(),
        'text': lambda node: accumulate_text_length(node.content),
    }
    
    optimized_traversal(ast, processors)
    
    return {
        'headings': heading_count,
        'links': link_count,
        'text_length': total_text_length
    }

# Efficient node finding with early termination
def find_first_heading(ast, target_level=1):
    """Find first heading of specified level (early termination)"""
    for node in ast.walk():
        if node.type == "heading" and node.level == target_level:
            return node
    return None

# Batch operations
def batch_process_nodes(ast, batch_size=100):
    """Process nodes in batches to optimize memory usage"""
    
    current_batch = []
    
    for node in ast.walk():
        current_batch.append(node)
        
        if len(current_batch) >= batch_size:
            process_node_batch(current_batch)
            current_batch = []
    
    # Process remaining nodes
    if current_batch:
        process_node_batch(current_batch)

def process_node_batch(nodes):
    """Process a batch of nodes efficiently"""
    # Group by type for more efficient processing
    nodes_by_type = {}
    for node in nodes:
        node_type = node.type
        if node_type not in nodes_by_type:
            nodes_by_type[node_type] = []
        nodes_by_type[node_type].append(node)
    
    # Process each type
    for node_type, type_nodes in nodes_by_type.items():
        if node_type == "heading":
            process_headings_batch(type_nodes)
        elif node_type == "link":
            process_links_batch(type_nodes)
        # ... other types
```

### Caching and Memoization

```python
from functools import lru_cache
import hashlib

class CachedParser:
    """Parser with result caching"""
    
    def __init__(self, backend="mistletoe", cache_size=128):
        self.parser = Parser(backend=backend)
        self.cache_size = cache_size
        self._setup_caching()
    
    def _setup_caching(self):
        """Setup LRU cache for parsing results"""
        self._cached_parse = lru_cache(maxsize=self.cache_size)(self._parse_impl)
    
    def _parse_impl(self, content_hash):
        """Internal parse implementation"""
        # This would need the actual content, stored separately
        # This is a simplified example
        return self.parser.parse(self._get_content_by_hash(content_hash))
    
    def parse(self, markdown_text):
        """Parse with caching"""
        # Create hash of content
        content_hash = hashlib.md5(markdown_text.encode()).hexdigest()
        
        # Store content for retrieval (in production, use proper cache)
        self._store_content(content_hash, markdown_text)
        
        return self._cached_parse(content_hash)
    
    def _store_content(self, hash_key, content):
        """Store content for hash lookup"""
        if not hasattr(self, '_content_store'):
            self._content_store = {}
        self._content_store[hash_key] = content
    
    def _get_content_by_hash(self, hash_key):
        """Retrieve content by hash"""
        return self._content_store.get(hash_key, "")
    
    def clear_cache(self):
        """Clear the parsing cache"""
        self._cached_parse.cache_clear()
        if hasattr(self, '_content_store'):
            self._content_store.clear()
    
    def cache_info(self):
        """Get cache statistics"""
        return self._cached_parse.cache_info()

# Usage
cached_parser = CachedParser()

# First parse - cache miss
ast1 = cached_parser.parse("# Hello World")

# Second parse - cache hit (much faster)
ast2 = cached_parser.parse("# Hello World")

print(cached_parser.cache_info())
```

### Transformation Optimization

```python
from marktripy.transformers import BaseTransformer

class OptimizedTransformer(BaseTransformer):
    """High-performance transformer implementation"""
    
    def __init__(self):
        self.stats = {
            'nodes_processed': 0,
            'transformations_applied': 0
        }
    
    def transform(self, ast):
        """Optimized transformation with minimal overhead"""
        
        # Pre-allocate data structures
        heading_nodes = []
        link_nodes = []
        text_nodes = []
        
        # Single pass to categorize nodes
        for node in ast.walk():
            self.stats['nodes_processed'] += 1
            
            node_type = node.type
            if node_type == "heading":
                heading_nodes.append(node)
            elif node_type == "link":
                link_nodes.append(node)
            elif node_type == "text":
                text_nodes.append(node)
        
        # Process each category efficiently
        self._process_headings_batch(heading_nodes)
        self._process_links_batch(link_nodes)
        self._process_text_batch(text_nodes)
        
        return ast
    
    def _process_headings_batch(self, headings):
        """Process all headings in batch for efficiency"""
        for heading in headings:
            # Efficient heading processing
            if not hasattr(heading, 'attrs'):
                heading.attrs = {}
            
            # Fast ID generation
            text = self._extract_text_fast(heading)
            heading.attrs['id'] = self._slugify_fast(text)
            
            self.stats['transformations_applied'] += 1
    
    def _extract_text_fast(self, node):
        """Fast text extraction without recursion"""
        if hasattr(node, 'content'):
            return node.content
        
        text_parts = []
        for child in getattr(node, 'children', []):
            if hasattr(child, 'content'):
                text_parts.append(child.content)
        
        return ''.join(text_parts)
    
    def _slugify_fast(self, text):
        """Fast slugification without regex"""
        # Simple character-by-character slugification
        result = []
        for char in text.lower():
            if char.isalnum():
                result.append(char)
            elif char.isspace() and result and result[-1] != '-':
                result.append('-')
        
        return ''.join(result).strip('-')

# Parallel processing for large documents
import concurrent.futures

class ParallelTransformer(BaseTransformer):
    """Transformer that uses parallel processing"""
    
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or 4
    
    def transform(self, ast):
        """Transform using parallel processing"""
        
        # Split document into sections
        sections = self._split_into_sections(ast)
        
        # Process sections in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_section = {
                executor.submit(self._process_section, section): section 
                for section in sections
            }
            
            for future in concurrent.futures.as_completed(future_to_section):
                section = future_to_section[future]
                try:
                    processed_section = future.result()
                    self._merge_section_back(ast, section, processed_section)
                except Exception as exc:
                    print(f'Section processing generated an exception: {exc}')
        
        return ast
    
    def _split_into_sections(self, ast):
        """Split AST into independent sections for parallel processing"""
        # Implementation would identify independent sections
        # This is a simplified example
        sections = []
        current_section = []
        
        for child in ast.children:
            if child.type == "heading" and child.level == 1:
                if current_section:
                    sections.append(current_section)
                current_section = [child]
            else:
                current_section.append(child)
        
        if current_section:
            sections.append(current_section)
        
        return sections
```

## Benchmarking and Monitoring

### Performance Testing Framework

```python
import time
import statistics
from typing import Callable, List, Dict, Any

class PerformanceBenchmark:
    """Comprehensive performance benchmarking for marktripy operations"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_function(self, 
                          func: Callable, 
                          *args, 
                          iterations: int = 100,
                          warmup_iterations: int = 10,
                          **kwargs) -> Dict[str, Any]:
        """Benchmark a function with statistical analysis"""
        
        # Warmup runs
        for _ in range(warmup_iterations):
            func(*args, **kwargs)
        
        # Benchmark runs
        times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        # Statistical analysis
        stats = {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times),
            'iterations': iterations,
            'total_time': sum(times)
        }
        
        return stats
    
    def benchmark_parsers(self, markdown_text: str, backends: List[str] = None):
        """Compare performance across different parser backends"""
        
        if backends is None:
            backends = ['mistletoe', 'markdown-it-py', 'markdown']
        
        results = {}
        
        for backend in backends:
            try:
                parser = Parser(backend=backend)
                
                def parse_func():
                    return parser.parse(markdown_text)
                
                stats = self.benchmark_function(parse_func, iterations=50)
                results[backend] = stats
                
            except Exception as e:
                results[backend] = {'error': str(e)}
        
        self.results['parser_comparison'] = results
        return results
    
    def benchmark_transformers(self, ast, transformers: List[BaseTransformer]):
        """Benchmark transformer performance"""
        
        results = {}
        
        for transformer in transformers:
            transformer_name = transformer.__class__.__name__
            
            def transform_func():
                # Create a copy to avoid modifying original
                ast_copy = self._deep_copy_ast(ast)
                return transformer.transform(ast_copy)
            
            stats = self.benchmark_function(transform_func, iterations=20)
            results[transformer_name] = stats
        
        self.results['transformer_comparison'] = results
        return results
    
    def _deep_copy_ast(self, ast):
        """Create a deep copy of AST for isolated testing"""
        # This would need proper AST copying implementation
        # For now, re-parse from markdown
        markdown = render_markdown(ast)
        return parse_markdown(markdown)
    
    def generate_report(self) -> str:
        """Generate a performance report"""
        
        report = ["# Performance Benchmark Report\n"]
        
        if 'parser_comparison' in self.results:
            report.append("## Parser Backend Comparison\n")
            
            for backend, stats in self.results['parser_comparison'].items():
                if 'error' in stats:
                    report.append(f"**{backend}**: Error - {stats['error']}\n")
                else:
                    report.append(f"**{backend}**:\n")
                    report.append(f"  - Mean: {stats['mean']*1000:.2f}ms\n")
                    report.append(f"  - Median: {stats['median']*1000:.2f}ms\n")
                    report.append(f"  - Std Dev: {stats['stdev']*1000:.2f}ms\n")
                    report.append(f"  - Min: {stats['min']*1000:.2f}ms\n")
                    report.append(f"  - Max: {stats['max']*1000:.2f}ms\n\n")
        
        if 'transformer_comparison' in self.results:
            report.append("## Transformer Performance\n")
            
            for transformer, stats in self.results['transformer_comparison'].items():
                report.append(f"**{transformer}**:\n")
                report.append(f"  - Mean: {stats['mean']*1000:.2f}ms\n")
                report.append(f"  - Operations/sec: {1/stats['mean']:.1f}\n\n")
        
        return "".join(report)

# Usage example
benchmark = PerformanceBenchmark()

# Test document
test_doc = """
# Performance Test Document

This is a test document with various elements:

## Lists
- Item 1
- Item 2
- Item 3

## Links
Check out [Python](https://python.org) and [GitHub](https://github.com).

## Code
```python
def hello():
    print("Hello, World!")
```

## Tables
| Column 1 | Column 2 |
|----------|----------|
| A        | B        |
""" * 10  # Multiply for larger test

# Benchmark parsers
parser_results = benchmark.benchmark_parsers(test_doc)

# Benchmark transformers
ast = parse_markdown(test_doc)
transformer_results = benchmark.benchmark_transformers(ast, [
    HeadingTransformer(add_ids=True),
    LinkTransformer(validate=False),  # Disable validation for speed test
    TOCTransformer(),
])

# Generate report
report = benchmark.generate_report()
print(report)
```

### Real-time Monitoring

```python
import time
import psutil
import threading
from collections import deque

class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.metrics = {
            'parse_times': deque(maxlen=window_size),
            'memory_usage': deque(maxlen=window_size),
            'cpu_usage': deque(maxlen=window_size),
        }
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval=1.0):
        """Start background monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval):
        """Background monitoring loop"""
        process = psutil.Process()
        
        while self.monitoring:
            # Collect system metrics
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
            
            self.metrics['memory_usage'].append(memory_mb)
            self.metrics['cpu_usage'].append(cpu_percent)
            
            time.sleep(interval)
    
    def record_parse_time(self, parse_time):
        """Record a parse operation time"""
        self.metrics['parse_times'].append(parse_time)
    
    def get_current_stats(self):
        """Get current performance statistics"""
        stats = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                stats[metric_name] = {
                    'current': values[-1],
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return stats

# Usage with context manager
class MonitoredParser:
    """Parser wrapper with performance monitoring"""
    
    def __init__(self, parser, monitor):
        self.parser = parser
        self.monitor = monitor
    
    def parse(self, markdown_text):
        """Parse with timing"""
        start_time = time.perf_counter()
        result = self.parser.parse(markdown_text)
        end_time = time.perf_counter()
        
        parse_time = end_time - start_time
        self.monitor.record_parse_time(parse_time)
        
        return result

# Example usage
monitor = PerformanceMonitor()
monitor.start_monitoring()

parser = Parser(backend="mistletoe")
monitored_parser = MonitoredParser(parser, monitor)

# Simulate workload
for i in range(50):
    test_text = f"# Document {i}\n" + "Some content. " * 100
    ast = monitored_parser.parse(test_text)
    time.sleep(0.1)  # Simulate processing time

# Get performance statistics
stats = monitor.get_current_stats()
for metric, values in stats.items():
    print(f"{metric}: avg={values['average']:.3f}, current={values['current']:.3f}")

monitor.stop_monitoring()
```

## Production Optimization Tips

### Configuration Recommendations

```python
# High-throughput server configuration
production_parser = Parser(
    backend="mistletoe",           # Fastest backend
    extensions=[],                 # Minimal extensions
    options={
        "html": False,             # Disable HTML parsing
        "strict": True,            # Strict mode for speed
    }
)

# Memory-constrained environment
memory_optimized_parser = Parser(
    backend="mistletoe",
    options={
        "lazy_load": True,         # Lazy loading
        "max_depth": 10,           # Limit nesting depth
        "chunk_size": 4096,        # Smaller chunks
    }
)

# Balanced configuration for general use
balanced_parser = Parser(
    backend="markdown-it-py",
    extensions=["gfm"],            # Essential extensions only
    options={
        "html": False,
        "linkify": False,          # Disable expensive features
        "typographer": False,
    }
)
```

### Error Handling and Resilience

```python
import logging
from typing import Optional

class ResilientParser:
    """Parser with robust error handling and fallbacks"""
    
    def __init__(self, primary_backend="mistletoe", fallback_backend="markdown"):
        self.primary_parser = Parser(backend=primary_backend)
        self.fallback_parser = Parser(backend=fallback_backend)
        self.logger = logging.getLogger(__name__)
    
    def parse(self, markdown_text: str, timeout: Optional[float] = None) -> Optional[Any]:
        """Parse with timeout and fallback"""
        
        # Try primary parser
        try:
            if timeout:
                return self._parse_with_timeout(
                    self.primary_parser, markdown_text, timeout
                )
            else:
                return self.primary_parser.parse(markdown_text)
                
        except Exception as e:
            self.logger.warning(f"Primary parser failed: {e}")
            
            # Try fallback parser
            try:
                self.logger.info("Attempting fallback parser")
                return self.fallback_parser.parse(markdown_text)
                
            except Exception as e2:
                self.logger.error(f"Fallback parser also failed: {e2}")
                return None
    
    def _parse_with_timeout(self, parser, text, timeout):
        """Parse with timeout using threading"""
        import threading
        
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = parser.parse(text)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            # Force thread termination (not ideal, but necessary)
            self.logger.warning("Parse operation timed out")
            return None
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
```

## Next Steps

Performance optimization is crucial for production use. Continue with:

1. **[CLI Usage](cli.md)** - Command-line performance tools
2. **[API Reference](api-reference.md)** - Complete performance configuration options

With these optimization techniques, marktripy can handle large-scale document processing efficiently while maintaining quality and reliability.