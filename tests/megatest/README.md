# Notepad++ MCP Megatest Framework

Multi-level testing framework with production safety guarantees.

## 🏗️ Framework Overview

```
                    LEVEL 5: FULL BLAST
                    Real Notepad++ + Real output validation
                    Time: 60-120 min

               LEVEL 4: INTEGRATION
               Multi-tool workflows + Real data
               Time: 30-60 min

          LEVEL 3: ADVANCED
          All tools individually + Edge cases
          Time: 15-30 min

     LEVEL 2: STANDARD
     Core tools with mocks
     Time: 5-15 min

LEVEL 1: SMOKE
Quick sanity check
Time: 1-3 min
```

## 🛡️ Safety First

**ALL TESTS RUN IN ISOLATED ENVIRONMENTS**

- ✅ Never touches production Notepad++ installation
- ✅ Never modifies system files
- ✅ Automatic cleanup of test artifacts
- ✅ Production path detection and blocking
- ✅ Mock-based testing for CI environments

## 🚀 Quick Start

### Local Development

```bash
# Run smoke tests (2 min)
python scripts/run_megatest.py smoke

# Run standard tests (10 min)
python scripts/run_megatest.py standard

# Run with real Notepad++ (if installed)
python scripts/run_megatest.py standard --with-notepadpp

# Run all levels
python scripts/run_megatest.py all

# Generate coverage report
python scripts/run_megatest.py standard --coverage
```

### CI/CD (GitHub Actions)

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

```yaml
# Run specific level via workflow dispatch
Test Level: standard  # smoke, standard, advanced, integration, full
```

## 📋 Test Levels

### Level 1: Smoke Test (1-3 min)
**Purpose**: Quick sanity - does server work at all?

**Tests**:
- Server initialization
- Tool imports
- Basic file operations
- Path safety validation
- Mock environment setup

**Command**: `python scripts/run_megatest.py smoke`

---

### Level 2: Standard Test (5-15 min)
**Purpose**: Core functionality with mocks

**Tests**:
- All portmanteau tools (file_ops, text_ops, etc.)
- Mock-based Windows API calls
- Error handling
- Tool registration patterns
- Subprocess mocking

**Command**: `python scripts/run_megatest.py standard`

---

### Level 3: Advanced Test (15-30 min)
**Purpose**: Advanced features and edge cases

**Tests**:
- Complex operations
- Batch processing
- Configuration changes
- Performance benchmarks
- Error recovery

**Status**: Not implemented yet

---

### Level 4: Integration Test (30-60 min)
**Purpose**: Multi-tool workflows

**Tests**:
- Session save/load cycles
- Plugin discovery and installation
- Multi-file operations
- Workflow automation

**Status**: Not implemented yet

---

### Level 5: Full Blast Test (60-120 min)
**Purpose**: Complete validation with real Notepad++

**Tests**:
- Real Notepad++ instance
- Actual file operations
- UI automation validation
- Performance under load
- Real plugin testing

**Status**: Not implemented yet

## 🔧 Configuration

### Environment Variables

```bash
# Test environment
MEGATEST_MODE=local|ci

# Test location strategy
MEGATEST_LOCATION=local|hidden|visible|custom

# Cleanup strategy
MEGATEST_CLEANUP=immediate|on-success|archive

# Notepad++ availability
NOTEPADPP_AVAILABLE=0|1
```

### Local Configuration

Create `.env` file in project root:

```bash
# Megatest configuration
MEGATEST_LOCATION=local
MEGATEST_CLEANUP=on-success
```

## 🧪 Running Tests

### Prerequisites

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# For coverage reports
pip install pytest-cov
```

### Test Commands

```bash
# Run specific level
python scripts/run_megatest.py smoke
python scripts/run_megatest.py standard

# Run with options
python scripts/run_megatest.py standard --coverage --verbose

# Run with real Notepad++ (if available)
python scripts/run_megatest.py standard --with-notepadpp

# Keep test artifacts for debugging
python scripts/run_megatest.py standard --keep-results

# Continue all levels even if some fail
python scripts/run_megatest.py all --force-continue
```

### Test Results

Results are saved to `test-results/` directory:
- `coverage/` - HTML coverage reports
- `screenshots/` - UI test screenshots (Level 5)
- `artifacts/` - Test data and logs

## 🏗️ Test Structure

```
tests/megatest/
├── __init__.py                 # Framework documentation
├── conftest.py                 # Safety fixtures and mocks
├── shared/
│   └── mock_fixtures.py       # Shared mock objects
├── level1_smoke/
│   └── test_smoke_basic.py    # Quick sanity tests
├── level2_standard/
│   └── test_standard_core.py  # Core functionality tests
├── level3_advanced/           # (Not implemented)
├── level4_integration/        # (Not implemented)
└── level5_full/              # (Not implemented)
```

## 🔍 Mock Strategy

### Windows API Mocks

All Windows API calls are mocked for CI environments:

```python
# Mock win32api, win32con, win32gui
with patch('notepadpp_mcp.tools.controller.win32api') as mock_win32api:
    mock_win32api.SendMessage.return_value = 0
    mock_win32api.keybd_event = MagicMock()
```

### Subprocess Mocks

External commands (linting tools) are mocked:

```python
# Mock ruff, eslint, etc.
mock_subprocess.run.return_value = Mock(returncode=0, stdout='', stderr='')
```

### HTTP Mocks

Plugin API calls are mocked:

```python
# Mock plugin discovery API
mock_requests.get.return_value.json.return_value = {"plugins": [...]}
```

## 📊 Coverage

Current test coverage:

- **Level 1**: ✅ Implemented (15-20% coverage)
- **Level 2**: ✅ Implemented (35-45% coverage)
- **Level 3**: ❌ Not implemented (55-65% coverage)
- **Level 4**: ❌ Not implemented (75-85% coverage)
- **Level 5**: ❌ Not implemented (95-100% coverage)

## 🤝 Contributing

### Adding New Tests

1. Choose appropriate level directory
2. Follow naming convention: `test_*.py`
3. Use fixtures from `conftest.py`
4. Add safety assertions: `assert_production_safe(test_path)`

### Test Patterns

```python
@pytest.mark.megatest_smoke
async def test_basic_functionality(isolated_test_env, assert_production_safe):
    """Test: Basic functionality works."""
    test_dir = isolated_test_env["test_dir"]
    assert_production_safe(test_dir)

    # Test implementation
    result = await your_tool_function()
    assert result.success
```

## 🐛 Troubleshooting

### Common Issues

**Tests fail with "Production path detected"**
- Ensure test uses `isolated_test_env` fixture
- Check that test files are created in temp directories

**Mock errors in CI**
- Verify all Windows API calls are mocked
- Check that external dependencies are properly mocked

**Notepad++ not found**
- Tests are designed to work without Notepad++
- Use `--with-notepadpp` flag only when Notepad++ is installed

### Debug Mode

```bash
# Keep test artifacts
python scripts/run_megatest.py standard --keep-results

# Verbose output
python scripts/run_megatest.py standard --verbose

# Run specific test
pytest tests/megatest/level1_smoke/test_smoke_basic.py::test_server_initializes -v
```

## 📈 Performance

### Current Benchmarks

- **Level 1**: ~2 minutes
- **Level 2**: ~10 minutes
- **Level 3**: ~20 minutes (estimated)
- **Level 4**: ~45 minutes (estimated)
- **Level 5**: ~90 minutes (estimated)

### Optimization Tips

- Tests use parallel execution where possible
- Mock-heavy tests run faster in CI
- Real Notepad++ tests only run when requested

## 🎯 Next Steps

### Immediate Priorities

1. ✅ Implement Level 1 (Smoke)
2. ✅ Implement Level 2 (Standard)
3. ⏳ Implement Level 3 (Advanced)
4. ⏳ Implement Level 4 (Integration)
5. ⏳ Implement Level 5 (Full Blast)

### Future Enhancements

- Performance regression detection
- UI screenshot comparison
- Load testing with multiple Notepad++ instances
- Cross-platform testing (Windows/Linux/Mac)

---

## 📞 Support

### Getting Help

1. Check this README
2. Run `python scripts/run_megatest.py --help`
3. Check `docs/testing/` for detailed guides
4. Review CI logs in GitHub Actions

### Reporting Issues

- Test failures: Check `test-results/` directory
- Mock issues: Verify `conftest.py` fixtures
- Performance issues: Run with `--durations=10` flag

---

**Happy Testing! 🎉**

*Framework created for Notepad++ MCP - Safe, Fast, Comprehensive.*