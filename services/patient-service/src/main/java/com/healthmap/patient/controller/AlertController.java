package com.healthmap.patient.controller;

import com.healthmap.patient.dto.AlertDto;
import com.healthmap.patient.service.AlertService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/v1/alerts")
@RequiredArgsConstructor
public class AlertController {

    private final AlertService service;

    @PostMapping
    public ResponseEntity<AlertDto> createAlert(@Valid @RequestBody AlertDto dto) {
        return ResponseEntity.status(201).body(service.create(dto));
    }

    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<AlertDto>> getByPatient(@PathVariable String patientId) {
        return ResponseEntity.ok(service.getByPatient(patientId));
    }

    @GetMapping("/open")
    public ResponseEntity<List<AlertDto>> getOpen() {
        return ResponseEntity.ok(service.getOpen());
    }
}
