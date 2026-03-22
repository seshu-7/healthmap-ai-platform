package com.healthmap.patient.controller;

import com.healthmap.patient.dto.PatientDto;
import com.healthmap.patient.service.PatientService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import java.util.List;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class PatientControllerTest {

    @Autowired private MockMvc mvc;
    @MockBean private PatientService service;

    @Test
    void getPatient_returns200() throws Exception {
        PatientDto dto = PatientDto.builder().patientId("P001").firstName("John").lastName("Doe")
            .primaryCondition("CKD").conditions(List.of("CKD")).build();
        when(service.getById("P001")).thenReturn(dto);

        mvc.perform(get("/api/v1/patients/P001"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.patientId").value("P001"))
            .andExpect(jsonPath("$.firstName").value("John"));
    }

    @Test
    void getPatient_notFound_returns404() throws Exception {
        when(service.getById("X")).thenThrow(
            new com.healthmap.patient.exception.ResourceNotFoundException("Patient", "X"));

        mvc.perform(get("/api/v1/patients/X"))
            .andExpect(status().isNotFound());
    }

    @Test
    void search_returnsResults() throws Exception {
        PatientDto dto = PatientDto.builder().patientId("P001").firstName("John").conditions(List.of()).build();
        when(service.search("John")).thenReturn(List.of(dto));

        mvc.perform(get("/api/v1/patients/search").param("q", "John"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].patientId").value("P001"));
    }
}
