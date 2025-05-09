# 用戶偏好設定 API 使用指南

此文檔提供關於如何使用Everly後端API的用戶偏好設定功能的詳細說明。

## API 端點

### 獲取用戶偏好設定

```
GET /api/v1/users/me/preferences
```

**請求標頭：**
```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

**響應:**
```json
{
  "status": "success",
  "data": [
    {
      "key": "language",
      "value": "zh-TW"
    },
    {
      "key": "theme",
      "value": "dark"
    }
  ],
  "message": "User preferences retrieved successfully"
}
```

### 更新用戶偏好設定

```
PUT /api/v1/users/me/preferences
```

**請求標頭：**
```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
Content-Type: application/json
```

**請求正文：**
```json
{
  "language": "zh-TW",
  "theme": "dark",
  "custom_settings": {
    "notification_enabled": true,
    "font_size": 14
  }
}
```

**響應：**
```json
{
  "status": "success",
  "data": [
    {
      "key": "language",
      "value": "zh-TW"
    },
    {
      "key": "theme",
      "value": "dark"
    },
    {
      "key": "notification_enabled",
      "value": true
    },
    {
      "key": "font_size",
      "value": 14
    }
  ],
  "message": "User preferences updated successfully"
}
```

## 請求參數說明

`UserPreferenceUpdate` 模型支持以下參數：

| 參數 | 類型 | 必填 | 說明 |
|-----|------|------|------|
| language | string | 否 | 用戶界面語言偏好，例如 "en", "zh-TW" |
| theme | string | 否 | 用戶界面主題偏好，例如 "light", "dark" |
| custom_settings | object | 否 | 自定義用戶設置，可以包含任意鍵值對 |

## 二進制數據處理

當需要存儲二進制數據（如圖片）時，必須將其轉換為Base64字符串。例如：

```javascript
// 假設我們有一個二進制數據 (例如從文件讀取)
const binaryData = new Uint8Array([...]);

// 將其轉換為 Base64 字符串
const base64String = btoa(String.fromCharCode.apply(null, binaryData));

// 然後在請求中使用
const request = {
  custom_settings: {
    profileImage: base64String
  }
};

// 發送請求
fetch('/api/v1/users/me/preferences', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(request)
});
```

## 錯誤處理

### 常見錯誤

| 狀態碼 | 原因 | 解決方法 |
|-------|-----|---------|
| 400 | 提交的二進制數據未正確編碼 | 確保二進制數據使用Base64編碼 |
| 401 | 未認證或令牌無效 | 請確保提供有效的訪問令牌 |
| 500 | 服務器內部錯誤 | 請聯繫管理員或檢查日誌 |

### 錯誤響應示例

```json
{
  "status": "error",
  "code": "BINARY_DATA_ERROR",
  "message": "無法將二進制數據作為文本處理。請確保使用Base64編碼或適當的數據格式。"
}
```

## 最佳實踐

1. **增量更新**: 只發送需要更新的字段，不需要每次都發送所有偏好設定。

2. **緩存設定**: 在客戶端本地緩存偏好設定，減少API調用次數。

3. **異常處理**: 實現適當的錯誤處理機制，特別是在處理二進制數據時。

4. **資料驗證**: 在發送前驗證數據格式，特別是確保正確編碼二進制數據。

5. **使用 custom_settings**: 對於標準偏好之外的設定，使用 `custom_settings` 對象存儲，讓API更具擴展性。

## 常見問題

### Q: 如何清除某個偏好設定？
A: 將該設定的值設置為 `null` 並發送更新請求。例如 `{"theme": null}` 將清除主題設置。

### Q: 有偏好設定的大小限制嗎？
A: 對於單個偏好設定項目有10MB的限制，對於整個請求有50MB的限制。

### Q: 支持哪些數據類型？
A: 支持所有JSON兼容的數據類型：字符串、數字、布爾值、數組、對象，以及Base64編碼的二進制數據。 