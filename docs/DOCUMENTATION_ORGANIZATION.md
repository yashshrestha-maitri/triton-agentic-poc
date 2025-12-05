# Documentation Organization

This document explains the documentation structure and conventions for the Triton Agentic project.

---

## 📁 Folder Structure

All documentation has been organized into the `docs/` folder for better maintainability:

```
triton-agentic/
├── README.md                    # Main project overview (root level)
├── CLAUDE.md                    # Claude Code instructions (root level)
│
└── docs/                        # All documentation lives here
    ├── README.md                # Documentation index & navigation
    │
    ├── Getting Started
    │   ├── QUICKSTART.md
    │   └── DOCKER_SETUP.md
    │
    ├── API & Integration
    │   ├── API_README.md
    │   └── DATA_FLOW_EXPLANATION.md
    │
    ├── Features
    │   ├── PROSPECT_DATA_GENERATION.md
    │   ├── PROSPECT_DASHBOARD_SYSTEM.md
    │   ├── MESSAGE_BROKER_IMPLEMENTATION.md
    │   └── MESSAGE_BROKER_TESTING.md
    │
    ├── Operations
    │   ├── MONITORING_SETUP.md
    │   └── TESTING_AND_MONITORING_GUIDE.md
    │
    └── This File
        └── DOCUMENTATION_ORGANIZATION.md
```

---

## 📝 Documentation Conventions

### 1. File Naming

**Format:** `UPPERCASE_SNAKE_CASE.md`

**Examples:**
- ✅ `MESSAGE_BROKER_IMPLEMENTATION.md`
- ✅ `PROSPECT_DATA_GENERATION.md`
- ✅ `API_README.md`
- ❌ `message-broker.md`
- ❌ `readme.md` (lowercase)

### 2. File Locations

**Root Level (Only 2 files):**
- `README.md` - Main project overview
- `CLAUDE.md` - Claude Code instructions

**Documentation Folder (All other .md files):**
- `docs/README.md` - Documentation index
- `docs/FEATURE_NAME.md` - Feature documentation
- `docs/GUIDE_NAME.md` - Implementation guides

### 3. Internal Links

**From root to docs:**
```markdown
[Feature Documentation](./docs/FEATURE_NAME.md)
[Documentation Index](./docs/README.md)
```

**Between docs (same folder):**
```markdown
[Related Guide](./RELATED_GUIDE.md)
```

**From docs to root:**
```markdown
[Main README](../README.md)
```

---

## 📚 Documentation Types

### Getting Started Guides
- Quick setup instructions
- Step-by-step tutorials
- First-time user workflows

**Examples:**
- `QUICKSTART.md`
- `DOCKER_SETUP.md`

### Feature Documentation
- Detailed feature explanations
- Architecture and design decisions
- Usage examples and code snippets

**Examples:**
- `MESSAGE_BROKER_IMPLEMENTATION.md`
- `PROSPECT_DATA_GENERATION.md`

### Testing & Monitoring
- Testing procedures
- Monitoring setup
- Troubleshooting guides

**Examples:**
- `MESSAGE_BROKER_TESTING.md`
- `MONITORING_SETUP.md`

### API Reference
- Endpoint documentation
- Request/response schemas
- Authentication and errors

**Examples:**
- `API_README.md`

---

## ✍️ Creating New Documentation

### Step 1: Create the File

```bash
# Always create in docs/ folder
touch docs/NEW_FEATURE_NAME.md
```

### Step 2: Write Content

Use this template structure:

```markdown
# Feature Name

Brief description of the feature.

---

## Overview

What this feature does and why it exists.

## Architecture

How it works (diagrams, flow charts).

## Usage

Code examples and API calls.

## Testing

How to test this feature.

## Troubleshooting

Common issues and solutions.

---

## Related Documentation

- [Related Feature](./RELATED_FEATURE.md)
- [API Reference](./API_README.md)
```

### Step 3: Update Index

Add entry to `docs/README.md`:

```markdown
### New Section (if needed)

- **[New Feature](./NEW_FEATURE_NAME.md)** - Brief description
```

### Step 4: Link from Root (Optional)

If it's a major feature, add to root `README.md`:

```markdown
## 📚 Documentation

- **[New Feature Guide](./docs/NEW_FEATURE_NAME.md)** - Feature description
```

---

## 🔍 Finding Documentation

### By Topic

Use the **[Documentation Index](./README.md)** which organizes all docs by category.

### By Use Case

The index includes "Documentation by Use Case" sections for:
- New Developers
- DevOps/Infrastructure
- Frontend Developers
- Backend Developers

### By Search

```bash
# Search all documentation
grep -r "search term" docs/

# Search specific file
grep "search term" docs/SPECIFIC_FILE.md
```

---

## 🔗 Link Verification

To verify all internal links work:

```bash
# Find all markdown links
grep -r "\[.*\](\..*\.md)" docs/

# Check for broken links (manual verification)
# Click each link in your markdown viewer
```

---

## 📦 Benefits of This Organization

### Before (Root Level Clutter)
```
triton-agentic/
├── README.md
├── CLAUDE.md
├── QUICKSTART.md
├── API_README.md
├── DOCKER_SETUP.md
├── MONITORING_SETUP.md
├── MESSAGE_BROKER_IMPLEMENTATION.md
├── MESSAGE_BROKER_TESTING.md
├── PROSPECT_DATA_GENERATION.md
├── PROSPECT_DASHBOARD_SYSTEM.md
├── DATA_FLOW_EXPLANATION.md
├── TESTING_AND_MONITORING_GUIDE.md
└── ... (12 .md files in root!)
```

**Problems:**
- ❌ Cluttered root directory
- ❌ Hard to navigate
- ❌ No clear organization
- ❌ Difficult to find related docs

### After (Organized Structure)
```
triton-agentic/
├── README.md              # Clear entry point
├── CLAUDE.md              # Development guide
└── docs/                  # All documentation
    ├── README.md          # Documentation index
    └── ... (organized by category)
```

**Benefits:**
- ✅ Clean root directory
- ✅ Clear navigation via index
- ✅ Logical grouping by topic
- ✅ Easy to find related docs
- ✅ Scalable structure

---

## 🎯 Quick Reference

### Common Paths

| Purpose | Path |
|---------|------|
| Main project info | `README.md` |
| Development guide | `CLAUDE.md` |
| Documentation index | `docs/README.md` |
| Quick start | `docs/QUICKSTART.md` |
| API reference | `docs/API_README.md` |

### File Creation Commands

```bash
# Create new feature doc
touch docs/FEATURE_NAME.md

# Create new guide
touch docs/GUIDE_NAME.md

# Edit documentation index
nano docs/README.md
```

### Link Syntax

```markdown
# From root README to docs
[Documentation](./docs/README.md)
[Feature Guide](./docs/FEATURE_NAME.md)

# Between docs files
[Related Guide](./RELATED_GUIDE.md)
[Index](./README.md)

# From docs back to root
[Main README](../README.md)
```

---

## 📋 Checklist for New Documentation

When creating new documentation:

- [ ] File created in `docs/` folder (not root)
- [ ] Filename uses UPPERCASE_SNAKE_CASE
- [ ] Content follows template structure
- [ ] Added to `docs/README.md` index
- [ ] Added to root `README.md` (if major feature)
- [ ] Internal links use relative paths
- [ ] Code examples tested
- [ ] Diagrams included (if applicable)

---

## 🔄 Migration Complete

All documentation has been successfully reorganized:

✅ **10 files moved** from root to `docs/`
✅ **Documentation index created** (`docs/README.md`)
✅ **Root README updated** with docs links
✅ **CLAUDE.md updated** with conventions
✅ **Internal links verified** (all working)

---

## 📖 Next Steps

1. **Explore the docs:** Start with [docs/README.md](./README.md)
2. **Follow conventions:** Always create new docs in `docs/`
3. **Keep index updated:** Add new docs to `docs/README.md`
4. **Use clear names:** Descriptive UPPERCASE_SNAKE_CASE

---

**The documentation is now well-organized and easy to navigate! 📚**
