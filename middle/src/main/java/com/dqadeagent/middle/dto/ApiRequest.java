package com.dqadeagent.middle.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 前端统一请求参数
 */
public class ApiRequest {
    
    /**
     * 请求backend的路径（相对路径）
     */
    private String path;
    
    /**
     * 查询日期
     */
    @JsonProperty("queryDate")
    private String queryDate;
    
    /**
     * 开始日期
     */
    @JsonProperty("startDate")
    private String startDate;
    
    /**
     * 结束日期
     */
    @JsonProperty("endDate")
    private String endDate;
    
    /**
     * 业务流水号
     */
    @JsonProperty("bizSeq")
    private String bizSeq;

    // 默认构造函数
    public ApiRequest() {}

    // 带参数构造函数
    public ApiRequest(String path, String queryDate, String startDate, String endDate, String bizSeq) {
        this.path = path;
        this.queryDate = queryDate;
        this.startDate = startDate;
        this.endDate = endDate;
        this.bizSeq = bizSeq;
    }

    // Getters and Setters
    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public String getQueryDate() {
        return queryDate;
    }

    public void setQueryDate(String queryDate) {
        this.queryDate = queryDate;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public String getBizSeq() {
        return bizSeq;
    }

    public void setBizSeq(String bizSeq) {
        this.bizSeq = bizSeq;
    }

    @Override
    public String toString() {
        return "ApiRequest{" +
                "path='" + path + '\'' +
                ", queryDate='" + queryDate + '\'' +
                ", startDate='" + startDate + '\'' +
                ", endDate='" + endDate + '\'' +
                ", bizSeq='" + bizSeq + '\'' +
                '}';
    }
}