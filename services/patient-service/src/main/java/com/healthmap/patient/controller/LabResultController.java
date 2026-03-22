package com.healthmap.patient.controller;

import com.healthmap.patient.dto.LabResultDto;
import com.healthmap.patient.service.LabResultService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/labs")
@RequiredArgsConstructor
public class LabResultController {

    private final LabResultService service;

    @GetMapping("/{patientId}")
    public ResponseEntity<Map<String, Object>> getLabs(
            @PathVariable String patientId,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(defaultValue = "collected_date:desc") String sort) {
        List<LabResultDto> results = service.getByPatient(patientId, limit);
        return ResponseEntity.ok(Map.of("results", results));
    }

    @GetMapping("/{patientId}/abnormal")
    public ResponseEntity<List<LabResultDto>> getAbnormal(@PathVariable String patientId) {
        return ResponseEntity.ok(service.getAbnormalByPatient(patientId));
    }
}
