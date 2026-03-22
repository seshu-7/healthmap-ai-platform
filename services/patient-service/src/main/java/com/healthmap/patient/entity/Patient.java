package com.healthmap.patient.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "patients")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Patient {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "first_name", nullable = false)
    private String firstName;

    @Column(name = "last_name", nullable = false)
    private String lastName;

    @Column(name = "date_of_birth")
    private LocalDate dateOfBirth;

    private String gender;

    @Column(name = "primary_condition")
    private String primaryCondition;

    /** Comma-separated list of conditions (e.g., "CKD,hypertension") */
    private String conditions;

    @Column(name = "insurance_plan")
    private String insurancePlan;

    @Column(name = "assigned_coordinator")
    private String assignedCoordinator;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    void prePersist() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    void preUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
