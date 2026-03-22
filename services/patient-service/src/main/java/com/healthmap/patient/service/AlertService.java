package com.healthmap.patient.service;

import com.healthmap.patient.dto.AlertDto;
import com.healthmap.patient.entity.Alert;
import com.healthmap.patient.repository.AlertRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AlertService {

    private final AlertRepository repo;

    public AlertDto create(AlertDto dto) {
        Alert alert = Alert.builder()
            .id(dto.getAlertId() != null ? dto.getAlertId() : UUID.randomUUID().toString().substring(0, 12))
            .patientId(dto.getPatientId())
            .priority(dto.getPriority())
            .title(dto.getTitle())
            .description(dto.getDescription())
            .recommendedAction(dto.getRecommendedAction())
            .status("OPEN")
            .build();
        return toDto(repo.save(alert));
    }

    public List<AlertDto> getByPatient(String patientId) {
        return repo.findByPatientIdOrderByCreatedAtDesc(patientId).stream().map(this::toDto).toList();
    }

    public List<AlertDto> getOpen() {
        return repo.findByStatusOrderByCreatedAtDesc("OPEN").stream().map(this::toDto).toList();
    }

    private AlertDto toDto(Alert a) {
        return AlertDto.builder()
            .alertId(a.getId()).patientId(a.getPatientId())
            .priority(a.getPriority()).title(a.getTitle())
            .description(a.getDescription()).recommendedAction(a.getRecommendedAction())
            .status(a.getStatus())
            .createdAt(a.getCreatedAt() != null ? a.getCreatedAt().toString() : null)
            .build();
    }
}
