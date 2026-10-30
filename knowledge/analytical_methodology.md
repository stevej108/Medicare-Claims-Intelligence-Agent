# Analytical Methodology

## Analytical Population

The analytical dataset is based on the CMS Data Entrepreneurs'
Synthetic Public Use File (DE-SynPUF).

DE-SynPUF contains synthetic Medicare-style beneficiary and claims
data. The project uses Beneficiary Summary, Inpatient, Outpatient,
Carrier, and Prescription Drug Event data.

Claims are transformed into a longitudinal beneficiary-year
analytical dataset.

The primary analytical grain is:

beneficiary × year

Each row represents one beneficiary observed during one analytical
year.

## Member-Year Construction

Beneficiary Summary files from 2008, 2009, and 2010 are combined
into a longitudinal beneficiary-year population.

Detailed healthcare utilization is aggregated separately from four
claims sources:

- Inpatient Claims
- Outpatient Claims
- Carrier Claims
- Prescription Drug Events

The aggregated utilization measures are then joined to the
beneficiary-year population using:

DESYNPUF_ID + year

The beneficiary-year table is kept as the population spine so that
beneficiary-years without utilization in a particular care setting
remain represented.

## Inpatient Claims

Raw inpatient data can contain multiple segments for the same
CLM_ID.

The analysis therefore treats unique CLM_ID values as inpatient
claims rather than counting physical source rows.

Segmented inpatient claims are collapsed to one claim-level record
before beneficiary-year utilization is calculated.

Annual inpatient measures include:

- inpatient claim count
- inpatient utilization days
- average inpatient days
- inpatient utilization indicator

## Outpatient Claims

Outpatient claims can also contain multiple segments for the same
CLM_ID.

Claims are collapsed to one record per CLM_ID before annual
utilization is calculated.

The primary outpatient utilization measure is annual unique
outpatient claim count.

## Carrier Claims

Carrier records were validated as one record per CLM_ID in the
analytical source files.

Carrier claims are aggregated to beneficiary-year level using
unique CLM_ID counts.

Carrier utilization represents professional or physician-service
utilization within the project.

## Prescription Drug Events

Prescription Drug Events use PDE_ID as the event identifier.

Annual pharmacy measures include:

- prescription event count
- unique drug products
- quantity dispensed
- prescription days supply
- patient prescription cost
- total prescription cost

## Analytical Year Attribution

Claims are assigned to an analytical year based primarily on claim
service