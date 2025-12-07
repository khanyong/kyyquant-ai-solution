
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** auto_stock
- **Date:** 2025-12-05
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001
- **Test Name:** Landing Page Load and Responsiveness
- **Test Code:** [null](./null)
- **Test Error:** Test execution timed out after 15 minutes
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/b82949a7-b9e9-4c35-9297-3f8cd2004115
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002
- **Test Name:** LoginDialog Authentication Success
- **Test Code:** [null](./null)
- **Test Error:** Test execution timed out after 15 minutes
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/bf5e2814-da3b-4e45-b80c-5d1509b0762e
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003
- **Test Name:** LoginDialog Authentication Failure and Error Handling
- **Test Code:** [TC003_LoginDialog_Authentication_Failure_and_Error_Handling.py](./TC003_LoginDialog_Authentication_Failure_and_Error_Handling.py)
- **Test Error:** The task to verify the system's behavior when an incorrect username or password is entered during login could not be fully completed. The login dialog opened successfully, but attempts to input invalid credentials into the username and password fields repeatedly failed due to element interaction limitations. Therefore, the login failure and error message display could not be confirmed, nor could the Redux store state be verified. Further investigation or alternative input methods are needed to complete this test.
Browser Console Logs:
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/068c9ea1-46e9-4690-ab27-dca6cf55ccf6
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004
- **Test Name:** Session Persistence After Reload
- **Test Code:** [TC004_Session_Persistence_After_Reload.py](./TC004_Session_Persistence_After_Reload.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/0ec589c9-8482-4171-b096-1bf34a29850d
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005
- **Test Name:** Navigation and Route Protection
- **Test Code:** [TC005_Navigation_and_Route_Protection.py](./TC005_Navigation_and_Route_Protection.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/97b3d282-9d77-4833-bff5-1465d2de5045
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006
- **Test Name:** Strategy Builder Save and Load Strategies
- **Test Code:** [TC006_Strategy_Builder_Save_and_Load_Strategies.py](./TC006_Strategy_Builder_Save_and_Load_Strategies.py)
- **Test Error:** The Strategy Builder interface could not be accessed from the current page despite multiple attempts to click on relevant UI elements. The page remains stuck on the service introduction section. This prevents proceeding with creating, saving, and validating strategies as required. Please verify the application navigation or UI functionality manually or with developer support.
Browser Console Logs:
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/b9f7c064-e57d-467e-8d59-050f99a93931
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007
- **Test Name:** Backtesting Process and Results Display
- **Test Code:** [TC007_Backtesting_Process_and_Results_Display.py](./TC007_Backtesting_Process_and_Results_Display.py)
- **Test Error:** Reported the navigation issue preventing access to the backtesting page. Stopping further actions as the core task cannot proceed without this navigation.
Browser Console Logs:
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/494ddec3-0ab0-47d4-a64d-24fbaab0ee36
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008
- **Test Name:** Realtime Signal Monitor Updates
- **Test Code:** [TC008_Realtime_Signal_Monitor_Updates.py](./TC008_Realtime_Signal_Monitor_Updates.py)
- **Test Error:** Reported navigation issue preventing access to the Signal Monitor page. Stopping further testing as the critical page for verifying the Realtime Signal Monitor component is inaccessible.
Browser Console Logs:
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/89e2be89-fbf2-490b-b8a3-8a48518db08f
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009
- **Test Name:** Auto Trading Panels Functional Verification
- **Test Code:** [TC009_Auto_Trading_Panels_Functional_Verification.py](./TC009_Auto_Trading_Panels_Functional_Verification.py)
- **Test Error:** Testing stopped. The Auto Trading panel and order placement UI could not be accessed from the current page. The page only shows service introduction and feature descriptions without interactive controls. Further testing cannot proceed until navigation or UI issues are resolved.
Browser Console Logs:
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/50822187-3cc0-4ab6-8322-0d5b31d88786
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010
- **Test Name:** Market Overview Dashboard Data and Responsiveness
- **Test Code:** [TC010_Market_Overview_Dashboard_Data_and_Responsiveness.py](./TC010_Market_Overview_Dashboard_Data_and_Responsiveness.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/616e78ae-ffc1-4e14-bd5a-d1f65dd81b23
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC011
- **Test Name:** Investment Settings Save and Apply
- **Test Code:** [TC011_Investment_Settings_Save_and_Apply.py](./TC011_Investment_Settings_Save_and_Apply.py)
- **Test Error:** The task to ensure investment parameters are saved and applied could not be fully completed due to navigation issues. The Investment Settings page could not be accessed as clicking the available navigation led to unrelated pages. The issue has been reported. Task is now stopped.
Browser Console Logs:
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/c0a976f5-aae2-451a-b2be-ac4fea3fdce0
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC012
- **Test Name:** Performance Dashboard Metrics Accuracy
- **Test Code:** [TC012_Performance_Dashboard_Metrics_Accuracy.py](./TC012_Performance_Dashboard_Metrics_Accuracy.py)
- **Test Error:** The task to verify trading performance metrics update based on recent trading activity and portfolio changes could not be fully completed. Although the services page loaded correctly with visible sections for Auto Trading and Performance Analysis, no interactive elements were accessible to execute or simulate trades. Consequently, verification of updated metrics such as profit/loss, ROI, and win rate, as well as charts and visualizations, could not be performed. Further access or UI fixes may be required to complete this task successfully.
Browser Console Logs:
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/1b3bac4d-c5d8-4e42-a453-48e2c32acb05
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC013
- **Test Name:** Network Error Handling for API Calls
- **Test Code:** [TC013_Network_Error_Handling_for_API_Calls.py](./TC013_Network_Error_Handling_for_API_Calls.py)
- **Test Error:** The task to simulate and verify network or API errors during Supabase calls or other API interactions could not be completed. The login modal and login button elements required for testing were not accessible, and no error messages or retry options appeared. The app does not handle network or API errors gracefully with user feedback as required. Task stopped.
Browser Console Logs:
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
[ERROR] Warning: validateDOMNesting(...): %s cannot appear as a descendant of <%s>.%s <div> p 
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Chip2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:12157:17)
    at p
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Typography2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:8303:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3396:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at CardContent2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17647:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Paper2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:5920:17)
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Card2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:17322:17)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Grid3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:23893:22)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Container4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:2557:19)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at CommunityHighlightSection (http://localhost:3000/src/components/landing/CommunityHighlightSection.tsx:41:38)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at LandingPage (http://localhost:3000/src/components/landing/LandingPage.tsx:27:24)
    at div
    at http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:3988:49
    at Box4 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:877:19)
    at MainApp (http://localhost:3000/src/AppWithRouter.tsx:99:20)
    at RenderedRoute (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4103:5)
    at Routes (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4574:5)
    at Router (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:4517:15)
    at BrowserRouter (http://localhost:3000/node_modules/.vite/deps/react-router-dom.js?v=1966a8f9:5266:5)
    at App
    at DefaultPropsProvider (http://localhost:3000/node_modules/.vite/deps/chunk-LU3YXPTE.js?v=1966a8f9:9523:3)
    at RtlProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1562:5)
    at ThemeProvider (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1512:15)
    at ThemeProvider2 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:1652:15)
    at ThemeProvider3 (http://localhost:3000/node_modules/.vite/deps/@mui_material.js?v=1966a8f9:3755:12)
    at AuthProvider (http://localhost:3000/src/contexts/AuthContext.tsx:21:32)
    at Provider (http://localhost:3000/node_modules/.vite/deps/react-redux.js?v=1966a8f9:1125:3) (at http://localhost:3000/node_modules/.vite/deps/chunk-V5LT2MCF.js?v=1966a8f9:520:37)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/1846a949-730b-48fe-b4a6-d0fbe3d9ab68
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC014
- **Test Name:** Avoidance of Unnecessary Re-renders
- **Test Code:** [TC014_Avoidance_of_Unnecessary_Re_renders.py](./TC014_Avoidance_of_Unnecessary_Re_renders.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/d45448e3-3c2d-41e8-89cc-0240df3e842c/c1af9cee-f909-4cad-9e48-c830c44e14b7
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **28.57** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---