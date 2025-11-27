package com.dqadeagent.middle.service;

import com.dqadeagent.middle.dto.ApiRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.util.UriComponentsBuilder;
import org.json.JSONObject;
import org.json.JSONArray;

import java.net.URI;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.logging.Logger;

/**
 * 代理服务类
 * 负责将前端请求转发到后端API
 */
@Service
public class ProxyService {

    private static final Logger logger = Logger.getLogger(ProxyService.class.getName());
    
    @Value("${backend.base-url:http://localhost:8000}")
    private String backendBaseUrl;

    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    public ProxyService() {
        this.webClient = WebClient.builder().build();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * 转发请求到后端API
     * 
     * @param request 前端请求参数
     * @return 后端API响应
     */
    public Object forwardRequest(ApiRequest request) {
        try {
            logger.info("开始处理转发请求");
            logger.info("请求路径: " + request.getPath());
            logger.info("查询日期: " + request.getQueryDate());
            
            // 构建后端API URL（只包含路径，不包含查询参数）
            String backendUrl = buildBackendUrl(request.getPath());
            logger.info("构建的后端URL: " + backendUrl);
            
            // 构建请求体（转换为驼峰命名）
            Map<String, Object> requestBody = buildRequestBody(request);
            logger.info("构建的请求体: " + objectMapper.writeValueAsString(requestBody));

            // 使用新的postRequest方法调用后端
            logger.info("开始调用后端API");
            JSONObject response = postRequest(backendUrl, requestBody);
            logger.info("后端调用完成");
            
            if (response == null) {
                logger.severe("后端返回null响应");
                throw new RuntimeException("Backend returned null response");
            }
            
            logger.info("Backend response: " + response.toString());
            
            // 检查是否是数组响应
            if (response.has("_array_")) {
                // 如果是数组，直接返回数组
                logger.info("Detected array response");
                JSONArray array = response.getJSONArray("_array_");
                return jsonArrayToList(array);
            } else {
                // 如果是对象，检查是否有data字段并提取
                logger.info("Processing object response");
                if (response.has("data")) {
                    // 提取data字段的内容
                    logger.info("Extracting 'data' field from backend response");
                    Object dataValue = response.get("data");
                    if (dataValue instanceof JSONObject) {
                        logger.info("Data is JSONObject, converting to Map");
                        return jsonObjectToMap((JSONObject) dataValue);
                    } else if (dataValue instanceof JSONArray) {
                        logger.info("Data is JSONArray, converting to List");
                        return jsonArrayToList((JSONArray) dataValue);
                    } else {
                        logger.info("Data is primitive, returning as is");
                        return dataValue;
                    }
                } else {
                    // 如果没有data字段，返回整个对象
                    logger.info("No data field found, returning entire response");
                    Object result = jsonObjectToMap(response);
                    return result;
                }
            }

        } catch (Exception e) {
            logger.severe("转发请求失败: " + e.getMessage());
            logger.severe("异常类型: " + e.getClass().getName());
            e.printStackTrace();
            throw new RuntimeException("Failed to forward request to backend", e);
        }
    }

    /**
     * 构建后端API的URL
     * 
     * @param path API路径
     * @return 完整的后端API URL
     */
    private String buildBackendUrl(String path) {
        // 确保path以/api开头
        if (!path.startsWith("/api")) {
            path = "/api" + (path.startsWith("/") ? "" : "/") + path;
        }
        return backendBaseUrl + path;
    }

    /**
     * 构建请求体（转换为驼峰命名）
     * 
     * @param request 请求参数
     * @return 请求体Map（使用驼峰命名）
     */
    private Map<String, Object> buildRequestBody(ApiRequest request) {
        Map<String, Object> body = new HashMap<>();

        // 转换参数名：下划线命名 → 驼峰命名
        if (request.getQueryDate() != null && !request.getQueryDate().trim().isEmpty()) {
            body.put("queryDate", request.getQueryDate());  // query_date → queryDate
        }

        if (request.getStartDate() != null && !request.getStartDate().trim().isEmpty()) {
            body.put("startDate", request.getStartDate());  // start_date → startDate
        }

        if (request.getEndDate() != null && !request.getEndDate().trim().isEmpty()) {
            body.put("endDate", request.getEndDate());      // end_date → endDate
        }

        if (request.getBizSeq() != null && !request.getBizSeq().trim().isEmpty()) {
            body.put("bizSeq", request.getBizSeq());        // biz_seq → bizSeq
        }

        return body;
    }

    /**
     * 使用RestTemplate发送POST请求到后端API
     * 
     * @param urlString 请求URL
     * @param requestBody 请求体对象
     * @return JSONObject响应
     */
    public static JSONObject postRequest(String urlString, Object requestBody) {
        Logger logger = Logger.getLogger(ProxyService.class.getName());
        
        if (requestBody == null) {
            logger.info("requestBody is null");
        } else {
            logger.info("开始调用，requestBody：" + serializeToJson(requestBody));
            logger.info("开始调用，url：" + urlString);
        }
        
        RestTemplate restTemplate = new RestTemplate();
        
        // 设置请求头
        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "application/json");
        headers.set("authKey", "ea264056dffb4002bbd3d1e4a36bf727");
        headers.set("biz_key", UUID.randomUUID().toString());
        headers.set("Authorization", "Bearer app-GJX7pCngygOEWdZpTPpAQMx7");
        
        // 创建请求实体
        String jsonBody = serializeToJson(requestBody);
        HttpEntity<String> entity = new HttpEntity<>(jsonBody, headers);

        try {
            ResponseEntity<String> response = restTemplate.exchange(
                urlString, 
                HttpMethod.POST, 
                entity, 
                String.class
            );
            
            logger.info("response：" + response);
            if (response.getStatusCode().is2xxSuccessful()) {
                String responseBody = response.getBody();
                if (responseBody != null && !responseBody.trim().isEmpty()) {
                    // 检查响应是数组还是对象
                    responseBody = responseBody.trim();
                    if (responseBody.startsWith("[")) {
                        // 返回的是数组，直接放在一个简单对象中，不嵌套data
                        JSONObject result = new JSONObject();
                        result.put("_array_", new JSONArray(responseBody));
                        return result;
                    } else {
                        // 返回的是对象
                        return new JSONObject(responseBody);
                    }
                } else {
                    logger.warning("响应体为空");
                    return null;
                }
            } else {
                logger.info("请求失败，状态码：" + response.getStatusCode());
                logger.severe("响应体：" + response.getBody());
                return null;
            }
        } catch (Exception e) {
            logger.info("请求过程中发生异常：" + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 将对象序列化为JSON字符串
     * 
     * @param obj 要序列化的对象
     * @return JSON字符串
     */
    private static String serializeToJson(Object obj) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            return mapper.writeValueAsString(obj);
        } catch (Exception e) {
            return obj.toString();
        }
    }

    /**
     * 将JSONObject转换为Map
     * 
     * @param jsonObject JSONObject对象
     * @return Map对象
     */
    private Map<String, Object> jsonObjectToMap(JSONObject jsonObject) {
        Map<String, Object> map = new HashMap<>();
        for (String key : jsonObject.keySet()) {
            Object value = jsonObject.get(key);
            if (value instanceof JSONObject) {
                map.put(key, jsonObjectToMap((JSONObject) value));
            } else if (value instanceof JSONArray) {
                map.put(key, jsonArrayToList((JSONArray) value));
            } else {
                map.put(key, value);
            }
        }
        return map;
    }

    /**
     * 将JSONArray转换为List
     * 
     * @param jsonArray JSONArray对象
     * @return List对象
     */
    private java.util.List<Object> jsonArrayToList(JSONArray jsonArray) {
        java.util.List<Object> list = new java.util.ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            Object value = jsonArray.get(i);
            if (value instanceof JSONObject) {
                list.add(jsonObjectToMap((JSONObject) value));
            } else if (value instanceof JSONArray) {
                list.add(jsonArrayToList((JSONArray) value));
            } else {
                list.add(value);
            }
        }
        return list;
    }
}
