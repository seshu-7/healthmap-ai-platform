package com.healthmap.patient.controller;

import com.healthmap.patient.dto.PatientDto;
import com.healthmap.patient.service.PatientService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/v1/patients")
@RequiredArgsConstructor
public class PatientController {

    private final PatientService service;

    @GetMapping("/{id}")
    public ResponseEntity<PatientDto> getPatient(@PathVariable String id) {
        return ResponseEntity.ok(service.getById(id));
    }

    @GetMapping("/search")
    public ResponseEntity<List<PatientDto>> search(@RequestParam String q,
                                                    @RequestParam(defaultValue = "10") int limit) {
        List<PatientDto> results = service.search(q);
        return ResponseEntity.ok(results.stream().limit(limit).toList());
    }

    @GetMapping("/coordinator/{coordinatorId}")
    public ResponseEntity<List<PatientDto>> getByCoordinator(@PathVariable String coordinatorId) {
        return ResponseEntity.ok(service.getByCoordinator(coordinatorId));
    }

    @PostMapping
    public ResponseEntity<PatientDto> createPatient(@RequestBody PatientDto dto) {
        return ResponseEntity.status(201).body(service.create(dto));
    }
}
