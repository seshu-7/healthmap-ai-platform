package com.healthmap.patient.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class AlertDto {
    private String alertId;
    @NotBlank private String patientId;
    @NotBlank private String priority;
    @NotBlank private String title;
    private String description;
    private String recommendedAction;
    private String status;
    private String createdAt;
}
