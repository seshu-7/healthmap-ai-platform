package com.healthmap.patient.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "alerts")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Alert {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @Column(nullable = false)
    private String priority;  // ROUTINE, URGENT, CRITICAL

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "recommended_action", columnDefinition = "TEXT")
    private String recommendedAction;

    @Column(nullable = false)
    private String status;  // OPEN, ACKNOWLEDGED, RESOLVED

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "resolved_at")
    private LocalDateTime resolvedAt;

    @PrePersist
    void prePersist() {
        if (createdAt == null) createdAt = LocalDateTime.now();
        if (status == null) status = "OPEN";
    }
}
