# CLI Usage

Master the marktripy command-line interface for batch processing, validation, and automation. The CLI provides powerful tools for document transformation pipelines and integration with other systems.

## Basic CLI Commands

### Installation and Setup

```bash
# Install marktripy with CLI support
pip install marktripy

# Verify installation
marktripy --version

# Get help
marktripy --help
```

### Quick Conversion

```bash
# Convert Markdown to HTML
marktripy convert input.md --output output.html

# Convert to HTML with specific parser
marktripy convert input.md --output output.html --parser mistletoe

# Convert with extensions
marktripy convert input.md --output output.html --extensions gfm,kbd,math
```

## Document Conversion

### Basic Conversion Operations

```bash
# Markdown to HTML
marktripy convert document.md --to html --output document.html

# Markdown to Markdown (with transformations)
marktripy convert document.md --to markdown --output processed.md

# Convert multiple files
marktripy convert *.md --to html --output-dir html_output/

# Batch conversion with pattern
marktripy convert docs/**/*.md --to html --output-dir site/ --preserve-structure
```

### Advanced Conversion Options

```bash
# Convert with custom configuration
marktripy convert input.md \
  --parser markdown-it-py \
  --extensions gfm,tables,tasklists \
  --options '{"html": false, "linkify": true}' \
  --output result.html

# Convert with transformations
marktripy convert input.md \
  --transform add-heading-ids \
  --transform downgrade-headings \
  --transform validate-links \
  --output processed.md

# Stream processing for large files
marktripy convert large_file.md \
  --stream \
  --chunk-size 1048576 \
  --output processed_large.md
```

### Output Format Options

```bash
# HTML output with custom template
marktripy convert input.md \
  --to html \
  --template custom_template.html \
  --css styles.css \
  --output styled.html

# JSON AST output
marktripy convert input.md \
  --to json \
  --pretty \
  --output ast.json

# Plain text extraction
marktripy convert input.md \
  --to text \
  --strip-formatting \
  --output content.txt
```

## Document Transformation

### Built-in Transformations

```bash
# Add IDs to all headings
marktripy transform input.md --add-heading-ids --output output.md

# Downgrade heading levels
marktripy transform input.md --downgrade-headings 1 --output output.md

# Generate table of contents
marktripy transform input.md --add-toc --toc-max-level 3 --output output.md

# Validate and fix links
marktripy transform input.md --validate-links --fix-links --output output.md

# Combine multiple transformations
marktripy transform input.md \
  --add-heading-ids \
  --add-toc \
  --validate-links \
  --normalize-whitespace \
  --output fully_processed.md
```

### Custom Transformation Pipelines

```bash
# Use configuration file for complex pipelines
marktripy transform input.md --config transform_config.yaml --output output.md

# Example transform_config.yaml:
# transformations:
#   - type: heading
#     add_ids: true
#     downgrade: 1
#     normalize_hierarchy: true
#   - type: link
#     validate: true
#     add_external_indicators: true
#   - type: toc
#     max_level: 3
#     insert_position: "after_title"
#   - type: text
#     normalize_whitespace: true
#     fix_typography: true

# Apply transformation to directory
marktripy transform docs/ \
  --recursive \
  --pattern "*.md" \
  --config transform_config.yaml \
  --output-dir processed_docs/
```

### Interactive Transformation

```bash
# Interactive mode for step-by-step processing
marktripy transform input.md --interactive

# Preview transformations without applying
marktripy transform input.md --preview --add-heading-ids --add-toc

# Dry run to see what would be changed
marktripy transform docs/ --dry-run --recursive --validate-links
```

## Document Validation

### Content Validation

```bash
# Basic document validation
marktripy validate document.md

# Comprehensive validation
marktripy validate document.md \
  --check-links \
  --check-headings \
  --check-images \
  --check-tables \
  --check-syntax

# Validate multiple files
marktripy validate docs/**/*.md --recursive --summary

# Custom validation rules
marktripy validate document.md --rules validation_rules.yaml
```

### Link Validation

```bash
# Check all links (internal and external)
marktripy validate document.md --check-links --timeout 10

# Check only external links
marktripy validate document.md --check-external-links --parallel 5

# Check and report broken links
marktripy validate document.md \
  --check-links \
  --report broken_links.json \
  --fix-suggestions

# Validate links with custom headers
marktripy validate document.md \
  --check-links \
  --headers '{"User-Agent": "marktripy-validator"}' \
  --timeout 30
```

### Structure Validation

```bash
# Check heading hierarchy
marktripy validate document.md --check-heading-hierarchy

# Validate table structure
marktripy validate document.md --check-table-structure

# Check for required sections
marktripy validate document.md \
  --required-sections "Introduction,Usage,Examples" \
  --section-order strict

# Validate against schema
marktripy validate document.md --schema document_schema.json
```

## Analysis and Statistics

### Document Analysis

```bash
# Basic document statistics
marktripy analyze document.md

# Detailed analysis with metrics
marktripy analyze document.md \
  --metrics word-count,heading-count,link-count,reading-time \
  --output stats.json

# Compare multiple documents
marktripy analyze docs/*.md --compare --output comparison.html

# Generate content report
marktripy analyze document.md \
  --report \
  --include-toc \
  --include-links \
  --include-images \
  --output report.html
```

### Content Extraction

```bash
# Extract all headings
marktripy extract document.md --headings --output headings.txt

# Extract all links
marktripy extract document.md --links --format json --output links.json

# Extract table of contents
marktripy extract document.md --toc --max-level 3 --output toc.md

# Extract code blocks
marktripy extract document.md --code-blocks --language python --output code.py

# Extract specific sections
marktripy extract document.md \
  --sections "API Reference,Examples" \
  --output extracted_sections.md
```

### Search and Query

```bash
# Search for text patterns
marktripy search docs/ --pattern "TODO|FIXME" --recursive

# Search in specific elements
marktripy search document.md --headings --pattern "API"

# Search with regex
marktripy search document.md --regex "https?://\S+" --context 2

# Search and replace
marktripy search document.md \
  --pattern "old-api.com" \
  --replace "new-api.com" \
  --output updated.md
```

## Batch Processing

### Directory Operations

```bash
# Process entire directory structure
marktripy batch-process docs/ \
  --operation convert \
  --to html \
  --output-dir site/ \
  --preserve-structure \
  --parallel 4

# Apply transformations to all files
marktripy batch-process docs/ \
  --operation transform \
  --add-heading-ids \
  --add-toc \
  --recursive \
  --pattern "*.md"

# Validate all documentation
marktripy batch-process docs/ \
  --operation validate \
  --check-links \
  --check-headings \
  --recursive \
  --report validation_report.html
```

### Watch Mode

```bash
# Watch directory for changes and auto-process
marktripy watch docs/ \
  --command "convert --to html --output-dir site/" \
  --recursive \
  --ignore "*.tmp,*.bak"

# Watch with custom processing
marktripy watch docs/ \
  --command "transform --add-heading-ids --validate-links" \
  --debounce 1000 \
  --verbose
```

### Scripting and Automation

```bash
# Generate processing script
marktripy generate-script \
  --operations "transform,validate,convert" \
  --config pipeline_config.yaml \
  --output process_docs.sh

# Export configuration
marktripy export-config --operations all --output marktripy_config.yaml

# Import and run configuration
marktripy run-config marktripy_config.yaml --input docs/ --output processed/
```

## Integration and Workflows

### CI/CD Integration

```bash
# Validate documentation in CI
marktripy validate docs/ \
  --recursive \
  --check-links \
  --fail-on-error \
  --report junit_report.xml

# Build documentation site
marktripy build-site docs/ \
  --output site/ \
  --theme default \
  --nav auto \
  --search enable

# Generate deployment artifacts
marktripy package docs/ \
  --format zip \
  --include-assets \
  --output documentation.zip
```

### Git Integration

```bash
# Process only changed files
marktripy git-process \
  --since HEAD~1 \
  --operation validate \
  --check-links

# Pre-commit hook processing
marktripy pre-commit \
  --staged-files \
  --validate \
  --fix-auto-fixable \
  --add-to-stage

# Generate commit report
marktripy git-report \
  --since "1 week ago" \
  --include-stats \
  --output weekly_report.md
```

### External Tool Integration

```bash
# Export to various formats
marktripy export document.md \
  --format docx \
  --pandoc-args "--toc --standalone" \
  --output document.docx

# Integration with static site generators
marktripy jekyll-process docs/ \
  --add-front-matter \
  --generate-nav \
  --output _posts/

# Integration with documentation systems
marktripy mkdocs-process docs/ \
  --generate-nav \
  --add-metadata \
  --output mkdocs_site/
```

## Configuration and Customization

### Configuration Files

```yaml
# ~/.marktripy/config.yaml
parser:
  default_backend: mistletoe
  extensions:
    - gfm
    - kbd
    - math
  options:
    html: false
    linkify: true

transformations:
  default_pipeline:
    - type: heading
      add_ids: true
      normalize_hierarchy: true
    - type: link
      validate: true
      timeout: 10
    - type: toc
      max_level: 3

validation:
  check_links: true
  check_headings: true
  parallel_requests: 5
  timeout: 30

output:
  preserve_structure: true
  overwrite_existing: false
  backup_originals: true
```

### Custom Profiles

```bash
# Create custom profile
marktripy profile create api-docs \
  --parser markdown-it-py \
  --extensions gfm,kbd \
  --transform add-heading-ids,add-toc \
  --validate check-links

# Use profile
marktripy convert document.md --profile api-docs --output output.html

# List available profiles
marktripy profile list

# Export profile configuration
marktripy profile export api-docs --output api-docs-profile.yaml
```

### Plugin Management

```bash
# List available extensions
marktripy extensions list

# Install extension
marktripy extensions install marktripy-mermaid

# Enable extension
marktripy extensions enable mermaid

# Configure extension
marktripy extensions configure mermaid --config mermaid_config.yaml
```

## Performance and Debugging

### Performance Monitoring

```bash
# Benchmark operations
marktripy benchmark document.md \
  --operations parse,transform,render \
  --iterations 100 \
  --report benchmark_report.html

# Profile memory usage
marktripy profile-memory large_document.md \
  --operations all \
  --report memory_profile.json

# Monitor real-time performance
marktripy monitor docs/ \
  --operations all \
  --interval 1 \
  --dashboard web
```

### Debugging and Troubleshooting

```bash
# Verbose output for debugging
marktripy convert document.md --verbose --debug --output debug.html

# Trace AST transformations
marktripy transform document.md \
  --add-heading-ids \
  --trace \
  --output traced.md

# Validate parser output
marktripy debug-parse document.md \
  --parser markdown-it-py \
  --show-ast \
  --show-tokens

# Check configuration
marktripy doctor --check-config --check-extensions --check-dependencies
```

### Error Handling

```bash
# Continue on errors
marktripy batch-process docs/ \
  --operation validate \
  --continue-on-error \
  --error-log errors.log

# Fallback processing
marktripy convert document.md \
  --parser markdown-it-py \
  --fallback-parser mistletoe \
  --output output.html

# Recovery mode
marktripy recover corrupted_document.md \
  --strategy best-effort \
  --output recovered.md
```

## Advanced CLI Features

### Custom Commands

```bash
# Create custom command
marktripy create-command process-blog \
  --template blog_template.py \
  --install

# Use custom command
marktripy process-blog posts/ \
  --add-reading-time \
  --generate-tags \
  --output site/

# Manage custom commands
marktripy commands list
marktripy commands remove process-blog
```

### Scripting Support

```bash
# Output structured data for scripting
marktripy analyze document.md --format json --quiet

# Pipe-friendly operations
cat document.md | marktripy transform --stdin --add-heading-ids

# Exit codes for scripting
marktripy validate document.md --check-links --exit-code
echo $?  # 0 for success, 1 for errors
```

### Environment Integration

```bash
# Use environment variables
export MARKTRIPY_PARSER=mistletoe
export MARKTRIPY_EXTENSIONS=gfm,kbd
marktripy convert document.md  # Uses environment settings

# Docker integration
docker run -v $(pwd):/docs marktripy/cli convert /docs/input.md --output /docs/output.html

# Integration with make
make docs:
	marktripy batch-process src/ --operation convert --to html --output-dir dist/
```

## Examples and Use Cases

### Documentation Workflow

```bash
#!/bin/bash
# Complete documentation processing pipeline

# 1. Validate all documentation
echo "Validating documentation..."
marktripy validate docs/ --recursive --check-links --check-headings

# 2. Apply transformations
echo "Processing documentation..."
marktripy transform docs/ \
  --recursive \
  --add-heading-ids \
  --add-toc \
  --validate-links \
  --normalize-whitespace

# 3. Generate static site
echo "Building site..."
marktripy convert docs/ \
  --to html \
  --output-dir site/ \
  --preserve-structure \
  --template site_template.html

# 4. Generate reports
echo "Generating reports..."
marktripy analyze docs/ \
  --recursive \
  --report \
  --output documentation_report.html

echo "Documentation processing complete!"
```

### Blog Processing

```bash
#!/bin/bash
# Blog post processing workflow

# Process new blog posts
marktripy batch-process posts/ \
  --pattern "*.md" \
  --operation transform \
  --add-reading-time \
  --add-social-meta \
  --generate-excerpts

# Convert to HTML with blog template
marktripy convert posts/ \
  --to html \
  --template blog_template.html \
  --output-dir site/posts/ \
  --preserve-structure

# Generate blog index
marktripy generate-index posts/ \
  --template index_template.html \
  --sort-by date \
  --output site/index.html
```

## Best Practices

### Performance Tips

```bash
# Use streaming for large files
marktripy convert large_file.md --stream --chunk-size 1048576

# Parallel processing for multiple files
marktripy batch-process docs/ --parallel 8 --operation convert

# Use fastest parser for bulk operations
marktripy convert docs/ --parser mistletoe --extensions none
```

### Error Prevention

```bash
# Always validate before processing
marktripy validate input.md && marktripy transform input.md --add-heading-ids

# Use dry-run for testing
marktripy transform docs/ --dry-run --recursive --add-heading-ids

# Backup before in-place operations
marktripy transform document.md --backup --add-heading-ids --output document.md
```

### Integration Guidelines

```bash
# Use configuration files for consistency
marktripy convert docs/ --config production.yaml

# Set up proper logging for automation
marktripy batch-process docs/ --log-file processing.log --log-level info

# Use exit codes for CI/CD
marktripy validate docs/ --recursive --fail-fast --exit-code
```

## Next Steps

The CLI provides comprehensive tools for document processing automation. For more advanced usage:

1. **[API Reference](api-reference.md)** - Complete CLI command reference
2. **Extend with custom commands** - Create domain-specific processing tools
3. **Integration patterns** - Common CI/CD and workflow integrations

The marktripy CLI is designed to integrate seamlessly into any documentation workflow, from simple conversions to complex processing pipelines.