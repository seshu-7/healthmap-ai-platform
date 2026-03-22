package com.healthmap.patient.dto;

import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class MedicationDto {
    private String medicationId;
    private String patientId;
    private String drugName;
    private String dosage;
    private String frequency;
    private String prescriber;
    private String startDate;
    private Boolean isActive;
}
