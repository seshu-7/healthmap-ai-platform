package com.healthmap.patient.dto;

import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class LabResultDto {
    private String labId;
    private String patientId;
    private String testName;
    private Double value;
    private String unit;
    private String referenceRange;
    private Boolean isAbnormal;
    private String collectedDate;
}
