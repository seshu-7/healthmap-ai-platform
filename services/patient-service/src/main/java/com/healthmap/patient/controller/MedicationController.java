package com.healthmap.patient.controller;

import com.healthmap.patient.dto.MedicationDto;
import com.healthmap.patient.service.MedicationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/medications")
@RequiredArgsConstructor
public class MedicationController {

    private final MedicationService service;

    @GetMapping("/{patientId}")
    public ResponseEntity<Map<String, Object>> getMedications(
            @PathVariable String patientId,
            @RequestParam(defaultValue = "true") boolean activeOnly) {
        List<MedicationDto> meds = service.getByPatient(patientId, activeOnly);
        return ResponseEntity.ok(Map.of("medications", meds));
    }
}
