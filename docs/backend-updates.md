# Everly API 後端更新說明

## 更新概述

我們對後端認證流程進行了重要更新，改變了 Google OAuth 的實現方式。這些變更是為了解決 iOS 應用與後端 OAuth 客戶端不兼容的問題，並優化整體認證流程。

## 主要變更

1. **認證流程變更**：
   - 之前：前端獲取授權碼(code)，發送給後端；後端用授權碼換取訪問令牌
   - 現在：前端完成整個 OAuth 流程，直接獲取 Google 訪問令牌，發送給後端

2. **API 端點變更**：
   - 端點 URL 不變：`/api/v1/auth/google`
   - 請求體參數變更：由 `code` 變更為 `token`

3. **相關代碼變更**：
   - 移除了後端授權碼交換邏輯
   - 增強了 Google 令牌驗證功能
   - 更新了相關日誌記錄

## 前端需要的修改

### iOS 應用

1. **OAuth 流程變更**：
   - 之前：獲取授權碼後發送給後端
   - 現在：完成整個 OAuth 流程，獲取訪問令牌，然後發送給後端

2. **實施步驟**：
   
   a. 更新 Google 登錄按鈕處理邏輯：
   ```swift
   // 舊代碼
   func handleGoogleSignIn(code: String) {
       apiClient.authenticateWithGoogle(code: code) { result in
           // 處理結果
       }
   }
   
   // 新代碼
   func handleGoogleSignIn(token: String) {
       apiClient.authenticateWithGoogle(token: token) { result in
           // 處理結果
       }
   }
   ```
   
   b. 更新 API 客戶端代碼：
   ```swift
   // 舊代碼
   func authenticateWithGoogle(code: String, completion: @escaping (Result<User, Error>) -> Void) {
       let request = AuthRequest(code: code)
       post("/api/v1/auth/google", body: request) { (result: Result<AuthResponse, Error>) in
           // 處理結果
       }
   }
   
   // 新代碼
   func authenticateWithGoogle(token: String, completion: @escaping (Result<User, Error>) -> Void) {
       let request = AuthRequest(token: token)
       post("/api/v1/auth/google", body: request) { (result: Result<AuthResponse, Error>) in
           // 處理結果
       }
   }
   ```
   
   c. 更新模型定義：
   ```swift
   // 舊模型
   struct AuthRequest: Codable {
       let code: String
   }
   
   // 新模型
   struct AuthRequest: Codable {
       let token: String
   }
   ```

### 使用 Google Sign-In 的具體代碼範例

```swift
import GoogleSignIn

// 設置 Google 登錄
func setupGoogleSignIn() {
    GIDSignIn.sharedInstance.configuration = GIDConfiguration(clientID: "YOUR_CLIENT_ID")
}

// 處理登錄
func signInWithGoogle() {
    GIDSignIn.sharedInstance.signIn(withPresenting: self) { result, error in
        guard let result = result, error == nil else {
            // 處理錯誤
            return
        }
        
        // 舊方法：使用授權碼
        // let code = result.serverAuthCode
        // self.authenticateWithBackend(code: code)
        
        // 新方法：使用訪問令牌
        result.user.refreshTokensIfNeeded { user, error in
            guard let user = user, error == nil else {
                // 處理錯誤
                return
            }
            
            // 獲取訪問令牌
            let accessToken = user.accessToken.tokenString
            
            // 發送給後端
            self.authenticateWithBackend(token: accessToken)
        }
    }
}

// 與後端認證
func authenticateWithBackend(token: String) {
    apiClient.authenticateWithGoogle(token: token) { result in
        switch result {
        case .success(let user):
            // 登錄成功，保存用戶資訊和JWT令牌
            UserManager.shared.currentUser = user
            self.navigateToDashboard()
        case .failure(let error):
            // 處理錯誤
            self.showError(message: error.localizedDescription)
        }
    }
}
```

## 測試建議

1. **完整測試登錄流程**：
   - 確保可以成功獲取 Google 訪問令牌
   - 驗證後端能夠接受訪問令牌並返回 JWT
   - 檢查 JWT 能夠正確用於後續 API 請求

2. **錯誤情況測試**：
   - 測試發送過期令牌的情況
   - 測試發送格式不正確的令牌
   - 測試未登錄用戶訪問受保護資源

## 遷移時間表

- 發佈日期：2025-05-05
- 舊版 API 支持截止日期：2025-06-05（一個月過渡期）
- 所有客戶端需要在截止日期前完成更新

## 常見問題

**Q: 為什麼要進行這項變更？**  
A: iOS 應用的 OAuth 客戶端與後端使用的 OAuth 客戶端不兼容。移動應用通常沒有客戶端密鑰，因此無法在後端使用相同的客戶端進行令牌交換。新方法更符合安全最佳實踐。

**Q: 這會影響用戶體驗嗎？**  
A: 從用戶角度看，登錄體驗保持不變。變更僅影響前端和後端之間的通信方式。

**Q: 前端是否需要新的API密鑰？**  
A: 不需要。您可以繼續使用現有的 Google OAuth 客戶端 ID。

**Q: JWT令牌的格式和有效期有變化嗎？**  
A: 沒有。JWT令牌的格式、內容和有效期保持不變。

## 支持資源

如果您在實施過程中遇到任何問題，請聯繫：

- 技術支持：support@everly.app
- API文檔：https://api.everly.app/docs
- 開發者社區：https://community.everly.app

## 變更日誌

**2025-05-05**
- 更新認證流程，改為接受 Google 訪問令牌
- 增強令牌驗證和錯誤報告
- 更新API文檔 