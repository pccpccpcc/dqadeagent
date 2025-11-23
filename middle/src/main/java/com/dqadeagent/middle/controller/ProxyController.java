package com.dqadeagent.middle.controller;

import com.dqadeagent.middle.dto.ApiRequest;
import com.dqadeagent.middle.service.ProxyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 统一代理控制器
 * 前端所有请求都通过这个接口转发到后端
 */
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class ProxyController {

    @Autowired
    private ProxyService proxyService;

    /**
     * 统一代理接口
     * POST /api/proxy
     * 
     * @param request 包含路径和参数的请求对象
     * @return 后端API的响应
     */
    @PostMapping("/proxy")
    public ResponseEntity<Object> proxy(@RequestBody ApiRequest request) {
        try {
            // 验证请求参数
            if (request.getPath() == null || request.getPath().trim().isEmpty()) {
                Map<String, Object> errorMap = new HashMap<>();
                errorMap.put("error", "path parameter is required");
                return ResponseEntity.badRequest().body(errorMap);
            }

            // 调用代理服务转发请求，这里已经提取了data字段的内容
            Object data = proxyService.forwardRequest(request);
            
            // 构造统一的响应格式，将data包装在响应中
            Map<String, Object> response = new HashMap<>();
            response.put("data", data);
            response.put("code", 200);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            // 记录错误日志
            System.err.println("代理请求失败: " + e.getMessage());
            e.printStackTrace();
            
            // 返回错误响应
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Internal server error: " + e.getMessage());
            errorResponse.put("code", 500);
            
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * 健康检查接口
     */
    @GetMapping("/health")
    public ResponseEntity<Object> health() {
        return ResponseEntity.ok("{\"status\": \"ok\", \"message\": \"大乔工具运营数据管理台中间层\"}");
    }

    /**
     * 测试后端连接的简单接口
     */
    @PostMapping("/test-backend")
    public ResponseEntity<Object> testBackend() {
        try {
            // 直接测试调用后端
            String backendUrl = "http://localhost:8000/api/template-query/stats";
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("queryDate", "2025-11-05");
            
            org.json.JSONObject response = com.dqadeagent.middle.service.ProxyService.postRequest(backendUrl, requestBody);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", response != null ? response.toString() : "null");
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            errorResponse.put("stackTrace", java.util.Arrays.toString(e.getStackTrace()));
            
            return ResponseEntity.ok(errorResponse);
        }
    }
}
