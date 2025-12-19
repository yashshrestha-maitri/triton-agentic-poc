# Legacy Architecture Documentation

**Status:** Historical Reference Only
**Last Used:** Pre-2025
**Superseded By:** [Current Architecture](../architecture-current/)

---

## Overview

This folder contains documentation for the **old architecture** of the Triton platform, which was based on **value proposition-driven template generation**.

### Old Architecture Approach

```
Value Proposition (Text Description)
  ↓
Template Generator Agent
  ↓
Static Dashboard Templates
```

**Characteristics:**
- Qualitative value propositions (text descriptions)
- Hardcoded dashboard templates
- No mathematical ROI calculations
- Static, not data-driven
- Templates generated directly from text

---

## Why This Architecture Was Replaced

The old architecture had several limitations:

1. **No Quantitative Analysis**: Value propositions were qualitative descriptions, not mathematical models
2. **Static Templates**: Dashboard layouts were hardcoded, not data-driven
3. **No ROI Calculations**: No formulas or variables for calculating ROI
4. **Limited Flexibility**: Templates couldn't adapt to different ROI model types
5. **Manual Effort**: Significant manual work required to customize for each prospect

---

## Legacy Documentation Files

| File | Purpose | Status |
|------|---------|--------|
| [VALUE_PROPOSITION_SYSTEM.md](./VALUE_PROPOSITION_SYSTEM.md) | Value proposition extraction and management | **Deprecated** |
| [TRITON_ENGINEERING_SPEC.md](./TRITON_ENGINEERING_SPEC.md) | Original engineering specifications | **Reference Only** |
| [TRITON_IMPLEMENTATION_ROADMAP.md](./TRITON_IMPLEMENTATION_ROADMAP.md) | Original implementation roadmap | **Superseded** |

---

## Transition to New Architecture

The platform transitioned to the **ROI Model-driven architecture** in 2025, which provides:

✅ **Quantitative Models**: Mathematical ROI calculations with variables and formulas
✅ **13 Model Types**: B1-B13 specialized model types (Unit Price, Site of Care, etc.)
✅ **Data-Driven Dashboards**: Widgets populated from real prospect data
✅ **Dynamic Templates**: Dashboards generated from ROI model specifications
✅ **Automated Analysis**: AI-powered classification and model building

### Learn About Current Architecture

See the [Current Architecture](../architecture-current/) folder for:
- [TRITON_COMPLETE_FLOW.md](../architecture-current/TRITON_COMPLETE_FLOW.md) - Master reference
- [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](../architecture-current/ROI_MODEL_RESEARCH_FLOW_UPDATED.md) - ROI model system
- [TRITON_PLATFORM_WORKFLOW.md](../architecture-current/TRITON_PLATFORM_WORKFLOW.md) - 6-step workflow

---

## When to Reference Legacy Docs

You might reference these legacy docs when:

1. **Historical Context**: Understanding how the system evolved
2. **Migration Planning**: Comparing old vs new approaches
3. **Legacy Code**: Maintaining old code that hasn't been migrated yet
4. **Architecture Decisions**: Understanding why certain design choices were made

---

## Current Status

⚠️ **These documents are for historical reference only**

- Do NOT use for new development
- Do NOT update these files
- Refer to [architecture-current/](../architecture-current/) for active development

---

**For Current Documentation**: See [architecture-current/README.md](../architecture-current/README.md)
**For Main Documentation Index**: See [docs/README.md](../README.md)
