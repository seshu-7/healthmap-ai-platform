package com.healthmap.patient.dto;

import lombok.*;
import java.util.List;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class PatientDto {
    private String patientId;
    private String firstName;
    private String lastName;
    private String dateOfBirth;
    private String gender;
    private String primaryCondition;
    private List<String> conditions;
    private String insurancePlan;
    private String assignedCoordinator;
}
