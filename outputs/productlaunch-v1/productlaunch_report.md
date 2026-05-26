# productlaunch — Reverse Engineering Report

> **Auto-generated** by the Reverse Engineer Skill (Claude Code) · 2026-05-26 07:19 UTC
> Repository: [https://github.com/initcron/productlaunch](https://github.com/initcron/productlaunch)
> Primary Language: **Dotnet**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Codebase Metrics](#2-codebase-metrics)
3. [Architecture Overview](#3-architecture-overview)
4. [Module Inventory](#4-module-inventory)
5. [API Catalog](#5-api-catalog)
6. [Dependency Analysis](#6-dependency-analysis)
7. [Dead Code Analysis](#7-dead-code-analysis)
8. [Tech Debt Inventory](#8-tech-debt-inventory)
9. [Modernization Roadmap](#9-modernization-roadmap)
10. [Data Architecture & Microservices Decomposition](#10-data-architecture--microservices-decomposition)
11. [Risk Assessment](#11-risk-assessment)

---

## 1. Executive Summary

productlaunch is a legacy dotnet application with 73 source files, 59 classes, and 461 methods. Full AI analysis unavailable — set ANTHROPIC_API_KEY for richer insights.

| Attribute | Value |
|-----------|-------|
| **Architecture Pattern** | Monolithic (inferred) |
| **Modernization Priority** | HIGH |
| **Platform** | .NET / Windows Server |
| **Tech Stack** | `.NET Project File`, `.NET Solution`, `ASP.NET Framework (Legacy)` |
| **Total Files** | 73 |
| **Total Classes** | 59 |
| **Total Methods** | 461 |

**Priority Reasoning:**
Legacy codebases typically require prioritised modernisation planning.

---

## 2. Codebase Metrics

### Language Distribution

| Language | Files | Share |
|----------|-------|-------|
| Dotnet | 43 | 59% |
| Javascript | 30 | 41% |

### Key Counts

| Metric | Value |
|--------|-------|
| Files Analyzed | **73** |
| Classes Defined | **59** |
| Methods & Functions | **461** |
| API Endpoints Extracted | **0** |
| Unreferenced Files | **66** |
| Unreferenced Classes | **30** |
| External Dependencies | **27** |

---

## 3. Architecture Overview

**Pattern:** Monolithic (inferred)

### Architectural Layers Detected

- API / Presentation Layer
- Business Logic Layer
- Configuration / Bootstrap Layer
- Data Access Layer
- Utility / Shared Layer
- View / Template Layer

### Dependency Graph

```mermaid
graph TD
    Program --> ProductLaunch_Messaging
    Program --> ProductLaunch_Messaging_Messages_Events
    Program --> ProductLaunch_MessageHandlers_IndexProspect_Indexer
    Index --> ProductLaunch_MessageHandlers_IndexProspect_Documents
    Index --> Nest
    Program --> ProductLaunch_Model
    MessageHelper --> ProductLaunch_Messaging_Messages
    MessageQueue --> ProductLaunch_Messaging_Messages
    Global_asax --> ProductLaunch_Model_Initializers
    SignUp_aspx --> ProductLaunch_Model
    jquery_1_10_2 --> ___prev___
    jquery_1_10_2_min --> _l_
```

> The graph above shows inter-module dependencies extracted from import/using statements.
> Standard library imports are excluded.

---

## 4. Module Inventory

_Showing first 40 of 73 files._


#### `Env.cs`
- **Language**: Dotnet
- **Classes**: `Env`
- **Methods (top 5)**: `Get`
- **Dependencies**: 1 imports

#### `AssemblyInfo.cs`
- **Language**: Dotnet
- **Classes**: _none_
- **Methods (top 5)**: _none_
- **Dependencies**: 2 imports

#### `Country.cs`
- **Language**: Dotnet
- **Classes**: `Country`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `Prospect.cs`
- **Language**: Dotnet
- **Classes**: `Prospect`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `Role.cs`
- **Language**: Dotnet
- **Classes**: `Role`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `AssemblyInfo.cs`
- **Language**: Dotnet
- **Classes**: _none_
- **Methods (top 5)**: _none_
- **Dependencies**: 2 imports

#### `Config.cs`
- **Language**: Dotnet
- **Classes**: `Config`
- **Methods (top 5)**: `Get`
- **Dependencies**: 1 imports

#### `Program.cs`
- **Language**: Dotnet
- **Classes**: `Program`
- **Methods (top 5)**: `Main`, `IndexProspect`
- **Dependencies**: 5 imports

#### `Prospect.cs`
- **Language**: Dotnet
- **Classes**: `Prospect`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `Index.cs`
- **Language**: Dotnet
- **Classes**: `Index`
- **Methods (top 5)**: `Setup`, `CreateDocument`
- **Dependencies**: 3 imports

#### `AssemblyInfo.cs`
- **Language**: Dotnet
- **Classes**: _none_
- **Methods (top 5)**: _none_
- **Dependencies**: 2 imports

#### `Program.cs`
- **Language**: Dotnet
- **Classes**: `Program`
- **Methods (top 5)**: `Main`, `SaveProspect`
- **Dependencies**: 6 imports

#### `AssemblyInfo.cs`
- **Language**: Dotnet
- **Classes**: _none_
- **Methods (top 5)**: _none_
- **Dependencies**: 2 imports

#### `Config.cs`
- **Language**: Dotnet
- **Classes**: `Config`
- **Methods (top 5)**: `Get`
- **Dependencies**: 1 imports

#### `MessageHelper.cs`
- **Language**: Dotnet
- **Classes**: `MessageHelper`
- **Methods (top 5)**: _none_
- **Dependencies**: 2 imports

#### `MessageQueue.cs`
- **Language**: Dotnet
- **Classes**: `MessageQueue`
- **Methods (top 5)**: `CreateConnection`
- **Dependencies**: 1 imports

#### `Message.cs`
- **Language**: Dotnet
- **Classes**: `Message`
- **Methods (top 5)**: `Message`
- **Dependencies**: 0 imports

#### `ProspectSignedUpEvent.cs`
- **Language**: Dotnet
- **Classes**: `ProspectSignedUpEvent`
- **Methods (top 5)**: _none_
- **Dependencies**: 1 imports

#### `AssemblyInfo.cs`
- **Language**: Dotnet
- **Classes**: _none_
- **Methods (top 5)**: _none_
- **Dependencies**: 2 imports

#### `ProductLaunchContext.cs`
- **Language**: Dotnet
- **Classes**: `ProductLaunchContext`
- **Methods (top 5)**: `OnModelCreating`
- **Dependencies**: 1 imports

#### `StaticDataInitializer.cs`
- **Language**: Dotnet
- **Classes**: `StaticDataInitializer`
- **Methods (top 5)**: `Seed`, `AddCountry`, `AddRole`
- **Dependencies**: 1 imports

#### `AssemblyInfo.cs`
- **Language**: Dotnet
- **Classes**: _none_
- **Methods (top 5)**: _none_
- **Dependencies**: 2 imports

#### `About.aspx.cs`
- **Language**: Dotnet
- **Classes**: `About`
- **Methods (top 5)**: `Page_Load`
- **Dependencies**: 5 imports

#### `About.aspx.designer.cs`
- **Language**: Dotnet
- **Classes**: `About`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `Config.cs`
- **Language**: Dotnet
- **Classes**: `Config`
- **Methods (top 5)**: `Get`
- **Dependencies**: 1 imports

#### `Contact.aspx.cs`
- **Language**: Dotnet
- **Classes**: `Contact`
- **Methods (top 5)**: `Page_Load`
- **Dependencies**: 5 imports

#### `Contact.aspx.designer.cs`
- **Language**: Dotnet
- **Classes**: `Contact`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `Default.aspx.cs`
- **Language**: Dotnet
- **Classes**: `_Default`
- **Methods (top 5)**: `Page_Load`
- **Dependencies**: 3 imports

#### `Default.aspx.designer.cs`
- **Language**: Dotnet
- **Classes**: `_Default`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `Global.asax.cs`
- **Language**: Dotnet
- **Classes**: `Global`
- **Methods (top 5)**: `Application_Start`
- **Dependencies**: 6 imports

#### `SignUp.aspx.cs`
- **Language**: Dotnet
- **Classes**: `SignUp`
- **Methods (top 5)**: `PreloadStaticDataCache`, `Page_Load`, `PopulateRoles`, `PopulateCountries`, `btnGo_Click`
- **Dependencies**: 6 imports

#### `SignUp.aspx.designer.cs`
- **Language**: Dotnet
- **Classes**: `SignUp`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `Site.Master.cs`
- **Language**: Dotnet
- **Classes**: `SiteMaster`
- **Methods (top 5)**: `Page_Load`
- **Dependencies**: 5 imports

#### `Site.Master.designer.cs`
- **Language**: Dotnet
- **Classes**: `SiteMaster`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `Site.Mobile.Master.cs`
- **Language**: Dotnet
- **Classes**: `Site_Mobile`
- **Methods (top 5)**: `Page_Load`
- **Dependencies**: 6 imports

#### `Site.Mobile.Master.designer.cs`
- **Language**: Dotnet
- **Classes**: `Site_Mobile`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `ThankYou.aspx.cs`
- **Language**: Dotnet
- **Classes**: `ThankYou`
- **Methods (top 5)**: `Page_Load`
- **Dependencies**: 5 imports

#### `ThankYou.aspx.designer.cs`
- **Language**: Dotnet
- **Classes**: `ThankYou`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

#### `ViewSwitcher.ascx.cs`
- **Language**: Dotnet
- **Classes**: `ViewSwitcher`
- **Methods (top 5)**: `Page_Load`
- **Dependencies**: 8 imports

#### `ViewSwitcher.ascx.designer.cs`
- **Language**: Dotnet
- **Classes**: `ViewSwitcher`
- **Methods (top 5)**: _none_
- **Dependencies**: 0 imports

_...and 33 more files. See the SDD JSON for the complete inventory._


---

## 5. API Catalog

**Total Endpoints Extracted:** 0

_No API routes detected via static analysis. Routes may use dynamic registration patterns._

### OpenAPI 3.0 Specification

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "productlaunch API",
    "version": "1.0.0",
    "description": "Auto-extracted OpenAPI 3.0 spec from productlaunch"
  },
  "paths": {
    "/health": {
      "get": {
        "summary": "Health check",
        "responses": {
          "200": {
            "description": "OK"
          }
        }
      }
    }
  }
}
```

---

## 6. Dependency Analysis

### Top 10 Most Connected Modules

| Module | Outgoing References |
|--------|-------------------|
| `ViewSwitcher.ascx` | 8 |
| `Program` | 6 |
| `Global.asax` | 6 |
| `SignUp.aspx` | 6 |
| `Site.Mobile.Master` | 6 |
| `About.aspx` | 5 |
| `Contact.aspx` | 5 |
| `Site.Master` | 5 |
| `ThankYou.aspx` | 5 |
| `BundleConfig` | 5 |

### External Dependencies Sample

```
 + prev + 
+l+
Microsoft.AspNet.FriendlyUrls
Microsoft.AspNet.FriendlyUrls.Resolvers
Nest
ProductLaunch.MessageHandlers.IndexProspect.Documents
ProductLaunch.MessageHandlers.IndexProspect.Indexer
ProductLaunch.Messaging
ProductLaunch.Messaging.Messages
ProductLaunch.Messaging.Messages.Events
ProductLaunch.Model
ProductLaunch.Model.Initializers
System
System.Collections.Generic
System.Data.Entity
System.IO
System.Linq
System.Net
System.Runtime.CompilerServices
System.Runtime.InteropServices
System.Text
System.Threading
System.Web
System.Web.Optimization
System.Web.Routing
System.Web.UI
System.Web.UI.WebControls
```

---

## 7. Dead Code Analysis

> Static analysis heuristic — results require manual validation before deletion.

### Potentially Unreferenced Files (66)

- `Env.cs`
- `AssemblyInfo.cs`
- `Country.cs`
- `Prospect.cs`
- `Role.cs`
- `AssemblyInfo.cs`
- `Config.cs`
- `Prospect.cs`
- `AssemblyInfo.cs`
- `AssemblyInfo.cs`
- `Config.cs`
- `MessageQueue.cs`
- `Message.cs`
- `AssemblyInfo.cs`
- `ProductLaunchContext.cs`
- `AssemblyInfo.cs`
- `About.aspx.cs`
- `About.aspx.designer.cs`
- `Config.cs`
- `Contact.aspx.cs`

### Potentially Unreferenced Classes (30)

- `Env` in `Env.cs`
- `Country` in `Country.cs`
- `Prospect` in `Prospect.cs`
- `Role` in `Role.cs`
- `Config` in `Config.cs`
- `MessageHelper` in `MessageHelper.cs`
- `MessageQueue` in `MessageQueue.cs`
- `Message` in `Message.cs`
- `ProspectSignedUpEvent` in `ProspectSignedUpEvent.cs`
- `ProductLaunchContext` in `ProductLaunchContext.cs`
- `StaticDataInitializer` in `StaticDataInitializer.cs`
- `About` in `About.aspx.designer.cs`
- `Contact` in `Contact.aspx.designer.cs`
- `_Default` in `Default.aspx.designer.cs`
- `Global` in `Global.asax.cs`
- `SignUp` in `SignUp.aspx.designer.cs`
- `SiteMaster` in `Site.Master.designer.cs`
- `Site_Mobile` in `Site.Mobile.Master.designer.cs`
- `ThankYou` in `ThankYou.aspx.designer.cs`
- `ViewSwitcher` in `ViewSwitcher.ascx.designer.cs`

---

## 8. Tech Debt Inventory

- Legacy dependencies detected
- Documentation gaps
- Test coverage unknown

### Key Tech Debt Areas

| Area | Severity | Details |
|------|----------|---------|
| Legacy Dependencies | HIGH | 27 external deps — audit for CVEs and outdated versions |
| Documentation | MEDIUM | Auto-generated docs; manual review required for accuracy |
| Test Coverage | UNKNOWN | Test suite metrics not assessed |
| Dead Code | MEDIUM | 66 unreferenced files identified |
| API Documentation | HIGH | Full API documentation missing |

---

## 9. Modernization Roadmap

### Target Technology Stack

`ASP.NET Core 8`, `Entity Framework Core`, `Azure / AWS`, `Docker`, `Kubernetes`

### Migration Phases


**Phase 1: Assessment & Audit** `LOW risk` — _1-2 months_
  - Complete code audit
  - Map all dependencies
  - Identify critical paths

**Phase 2: Foundation & Refactoring** `MEDIUM risk` — _2-3 months_
  - Introduce unit tests
  - Refactor core modules
  - Upgrade dependencies

**Phase 3: Migration & Modernization** `HIGH risk` — _3-6 months_
  - Migrate to modern framework
  - Decompose monolith
  - CI/CD pipeline

**Phase 4: Validation & Launch** `MEDIUM risk` — _1-2 months_
  - End-to-end testing
  - Performance validation
  - Production cutover


### Proposed Microservice Boundaries

- **Core Domain Service**
- **API Gateway Service**
- **Auth & Identity Service**

### Risk Factors

- Breaking changes in major version upgrades
- Team retraining required
- Data migration complexity

**Estimated Total Effort:** 8-13 months

---

## 10. Data Architecture & Microservices Decomposition

> Entity definitions extracted by static analysis. Results depend on which files were included
> in the 300-file analysis cap. For large repos, run against a focused subset for best results.

### Schema Summary

| Metric | Value |
|--------|-------|
| Entities Detected | **3** |
| Relationships Detected | **0** |
| Bounded Contexts Identified | **3** |

### Detected Entities

| Entity | Table | Fields | Relationships |
|--------|-------|--------|---------------|
| `Country` | `Country` | 0 | 0 |
| `Role` | `Role` | 0 | 0 |
| `Prospect` | `Prospect` | 0 | 0 |

### Proposed Microservice Data Boundaries

Each bounded context below represents a candidate microservice that should own
its own dedicated database (**Database-Per-Service** pattern).

#### Configuration
Entities: `Country`

#### Customer / Identity
Entities: `Role`

#### Core / Infrastructure
Entities: `Prospect`


### Migration Guidance

When decomposing the monolithic database for microservices migration:

1. **Start with the loosest coupling** — identify entities with few cross-domain foreign keys.
2. **Introduce the Strangler Fig pattern** — new microservices own their tables, the monolith
   references them via API calls.
3. **Use the Outbox Pattern** for cross-service consistency — write events to an outbox table
   atomically, then publish via a message broker (e.g. RabbitMQ, Kafka).
4. **Avoid distributed transactions** — favour eventual consistency and compensating transactions.
5. **Data synchronisation phase** — run dual-write during transition; cut over once stable.

---

## 11. Risk Assessment

| Category | Severity | Description | Recommendation |
|----------|----------|-------------|----------------|
| Technical Debt | HIGH | 73 files with accumulated debt | Systematic refactoring backlog |
| Dead Code | MEDIUM | 66 unreferenced files | Review and prune |
| API Coverage | HIGH | 0 endpoints documented | Full OpenAPI spec required |
| Dependencies | MEDIUM | 27 external deps detected | CVE audit recommended |

---

## Appendix

### How This Report Was Generated

This report was produced by the **Reverse Engineer Skill** for Claude Code, which:

1. Cloned the repository from GitHub
2. Walked all source files (`.py`, `.java`, `.cs`, `.ts`, `.js`, etc.)
3. Applied regex-based AST extraction to identify classes, methods, imports, and API routes
4. Built a dependency graph from import/using statements
5. Applied dead-code heuristics (unreferenced module detection)
6. Generated an OpenAPI 3.0 specification from routing annotations
7. Used Claude claude-sonnet-4-6 for AI-powered executive summary and modernization planning

### Limitations

- Static analysis only — no runtime behaviour captured
- API extraction relies on common patterns (ASP.NET attributes, Spring annotations,
  Flask decorators, Express routes)
- Dead code detection is heuristic and may have false positives/negatives
- AI sections require `ANTHROPIC_API_KEY` for full content; fallback text used otherwise

---

_Generated by Reverse Engineer Skill · Claude Code · 2026-05-26 07:19 UTC_
