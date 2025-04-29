# Insurance Backend API

This document provides an overview and API reference for the Insurance Backend system built with Django REST Framework.

## Table of Contents

1.  [Core Concepts](#core-concepts)
2.  [Setup](#setup)
3.  [Authentication](#authentication)
4.  [API Endpoints](#api-endpoints)
    *   [Standard Endpoints (Router)](#standard-endpoints-router)
    *   [Custom Actions](#custom-actions)
5.  [Model API Formats](#model-api-formats)
    *   [User](#user-apiusers)
    *   [Occupation](#occupation-apioccupations)
    *   [MortalityRate](#mortalityrate-apimortality-rates)
    *   [Company](#company-apicompanies)
    *   [Branch](#branch-apibranches)
    *   [InsurancePolicy](#insurancepolicy-apiinsurance-policies)
    *   [GSVRate](#gsvrate-apigsv-rates)
    *   [SSVConfig](#ssvconfig-apissv-configs)
    *   [AgentApplication](#agentapplication-apiagent-applications)
    *   [SalesAgent](#salesagent-apisales-agents)
    *   [DurationFactor](#durationfactor-apiduration-factors)
    *   [Customer](#customer-apicustomers)
    *   [KYC](#kyc-apikyc)
    *   [PolicyHolder](#policyholder-apipolicy-holders)
    *   [BonusRate](#bonusrate-apibonus-rates)
    *   [Bonus](#bonus-apibonuses)
    *   [ClaimRequest](#claimrequest-apiclaim-requests)
    *   [ClaimProcessing](#claimprocessing-apiclaim-processing)
    *   [PaymentProcessing](#paymentprocessing-apipayment-processing)
    *   [Underwriting](#underwriting-apiunderwriting)
    *   [PremiumPayment](#premiumpayment-apipremium-payments)
    *   [AgentReport](#agentreport-apiagent-reports)
    *   [Loan](#loan-apiloans)
    *   [LoanRepayment](#loanrepayment-apiloan-repayments)
6.  [Permissions Overview](#permissions-overview)

## Core Concepts

This system manages various aspects of an insurance business:

*   **Configuration:** Defines core data like Occupations, Mortality Rates, Company details, Policy types (InsurancePolicy), GSV/SSV rates, Duration Factors, and Bonus Rates. These are typically managed by administrators.
*   **Structure:** Companies have Branches.
*   **Users:** The system uses a custom `User` model with types: `superadmin`, `branch` (Branch Admin), `agent` (Sales Agent), `customer`.
*   **Agents:** Potential agents apply via `AgentApplication`. Approved applications become `SalesAgent` records, linked to a User. Agents are associated with a Branch.
*   **Customers:** Customers register (`Customer` model), automatically creating a linked `User` record (username derived from email). Customers undergo `KYC` verification.
*   **Policies:** Customers become `PolicyHolder`s by taking out an `InsurancePolicy`. Policies are linked to the Customer, the specific Policy, an optional Agent, and the Branch. Policy details include duration, sum assured, health info, nominees, etc.
*   **Premiums:** `PremiumPayment` tracks payments made by PolicyHolders against their policies. Includes calculation of annual/interval premiums, GSV/SSV values.
*   **Bonuses:** `Bonus` records track bonuses accrued for customers based on `BonusRate`.
*   **Claims:** PolicyHolders can submit `ClaimRequest`s. These are reviewed via `ClaimProcessing` and, if approved, paid out via `PaymentProcessing`.
*   **Loans:** PolicyHolders can take out `Loan`s against their policy value (based on GSV). `LoanRepayment` tracks repayments.
*   **Underwriting:** `Underwriting` assesses the risk associated with a PolicyHolder.
*   **Reporting:** `AgentReport` tracks agent performance.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd insuranceBackend
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Apply migrations:**
    ```bash
    python manage.py migrate
    ```
5.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will typically be available at `http://127.0.0.1:8000/api/`.

## Authentication

The API uses Django REST Framework's **Token Authentication**.

1.  **Login:** Send a POST request to `/api/login/` with username and password.
    *   **Request Body:**
        ```json
        {
            "username": "your_username",
            "password": "your_password"
        }
        ```
    *   **Success Response (200 OK):**
        ```json
        {
            "token": "YOUR_AUTH_TOKEN_STRING",
            "user": {
                "user_id": 1,
                "username": "your_username",
                "email": "user@example.com",
                "first_name": "Test",
                "last_name": "User",
                "user_type": "customer" // or 'agent', 'branch', 'superadmin'
                // "branch_id": 5,      // Included for 'branch' users
                // "branch_name": "Main Branch", // Included for 'branch' users
                // "agent_id": 12       // Included for 'agent' users
            }
        }
        ```
2.  **Making Authenticated Requests:** Include the obtained token in the `Authorization` header for subsequent requests to protected endpoints:
    ```
    Authorization: Token YOUR_AUTH_TOKEN_STRING
    ```
3.  **Logout:** Send an authenticated POST request to `/api/logout/`.
    *   **Success Response (200 OK):**
        ```json
        {
            "detail": "Logged out successfully."
        }
        ```

## API Endpoints

The API follows REST principles and uses Django REST Framework's `DefaultRouter` for most models, providing standard CRUD operations.

### Standard Endpoints (Router)

For each model listed below (e.g., `users`), the following endpoints are typically available:

*   `GET /api/{model_name}/`: List all instances (subject to permissions).
*   `POST /api/{model_name}/`: Create a new instance.
*   `GET /api/{model_name}/{id}/`: Retrieve a specific instance.
*   `PUT /api/{model_name}/{id}/`: Update a specific instance (requires all fields).
*   `PATCH /api/{model_name}/{id}/`: Partially update a specific instance.
*   `DELETE /api/{model_name}/{id}/`: Delete a specific instance.

**Available Model Endpoints:**

*   `/api/users/`
*   `/api/occupations/`
*   `/api/mortality-rates/`
*   `/api/companies/`
*   `/api/branches/`
*   `/api/insurance-policies/`
*   `/api/gsv-rates/`
*   `/api/ssv-configs/`
*   `/api/agent-applications/`
*   `/api/sales-agents/`
*   `/api/duration-factors/`
*   `/api/customers/`
*   `/api/kyc/`
*   `/api/policy-holders/`
*   `/api/bonus-rates/`
*   `/api/bonuses/`
*   `/api/claim-requests/`
*   `/api/claim-processing/`
*   `/api/payment-processing/`
*   `/api/underwriting/`
*   `/api/premium-payments/`
*   `/api/agent-reports/`
*   `/api/loans/`
*   `/api/loan-repayments/`

### Custom Actions

Some models have additional actions:

*   **Customers:**
    *   `POST /api/customers/{id}/set_password/`: Sets the password for the customer's associated user. Requires `password` in the request body. (Owner/Admin access)
*   **Loans:**
    *   `POST /api/loans/{id}/accrue_interest/`: Triggers the interest accrual calculation for the loan. (Owner/Admin/Agent access)
*   **Claim Processing:**
    *   `POST /api/claim-processing/{id}/finalize/`: Finalizes the claim based on its current `processing_status` (Approved/Rejected). (Admin/Branch Admin access)

## Model API Formats

This section details the expected JSON structure for interacting with each model's API endpoint. Fields marked `read-only` are only included in responses, not expected in requests (POST/PUT/PATCH). Fields marked `write-only` are only expected in requests, not included in responses.

---

### User (`/api/users/`)

Represents system users.

*   **Fields:** `id` (read-only), `username`, `first_name`, `last_name`, `email`, `gender`, `phone`, `address`, `user_type`, `branch` (ID), `agent` (ID), `groups` (IDs), `user_permissions` (IDs), `is_active`, `is_staff` (read-only), `created_at` (read-only), `updated_at` (read-only), `last_login` (read-only), `password` (write-only).
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "gender": "Male",
        "phone": "1234567890",
        "address": "123 Main St",
        "user_type": "customer",
        "branch": null,
        "agent": null,
        "groups": [],
        "user_permissions": [],
        "is_active": true,
        "is_staff": false,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z",
        "last_login": "2023-10-27T11:00:00Z"
    }
    ```
*   **POST/PUT (Example):**
    ```json
    {
        "username": "janedoe",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "password": "a_strong_password", // Required on POST, optional on PUT/PATCH
        "gender": "Female",
        "phone": "0987654321",
        "address": "456 Oak Ave",
        "user_type": "agent", // Set user type
        "branch": 1, // Assign to Branch with ID 1
        "agent": 5,  // Assign to SalesAgent with ID 5 (relevant for agent user type)
        "is_active": true
    }
    ```

---

### Occupation (`/api/occupations/`)

Defines job roles and their associated risk.

*   **Fields:** `id` (read-only), `name`, `risk_category` (Choices: "Low", "Moderate", "High").
*   **GET/POST/PUT (Example):**
    ```json
    {
        "id": 1, // Read-only on GET
        "name": "Software Engineer",
        "risk_category": "Low"
    }
    ```

---

### MortalityRate (`/api/mortality-rates/`)

Defines mortality rates based on age groups.

*   **Fields:** `id` (read-only), `age_group_start`, `age_group_end`, `rate` (Decimal, e.g., "1.50").
*   **GET/POST/PUT (Example):**
    ```json
    {
        "id": 1, // Read-only on GET
        "age_group_start": 30,
        "age_group_end": 39,
        "rate": "0.85"
    }
    ```

---

### Company (`/api/companies/`)

Represents the insurance company itself.

*   **Fields:** `id` (read-only), `name`, `company_code`, `address`, `logo` (file upload/URL), `email`, `is_active`, `phone_number`.
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "name": "SecureLife Insurance",
        "company_code": 101,
        "address": "1 Corporate Drive",
        "logo": "/media/company/logo.png",
        "email": "info@securelife.com",
        "is_active": true,
        "phone_number": "+1-555-1000"
    }
    ```
*   **POST/PUT (Example):** (Logo handled via multipart/form-data)
    ```json
    {
        "name": "SecureLife Insurance",
        "company_code": 101,
        "address": "1 Corporate Drive",
        "email": "info@securelife.com",
        "is_active": true,
        "phone_number": "+1-555-1000"
    }
    ```

---

### Branch (`/api/branches/`)

Represents company branches.

*   **Fields:** `id` (read-only), `name`, `branch_code`, `location`, `company` (ID), `company_name` (read-only), `user` (ID of associated Branch Admin User), `user_details` (read-only, nested User object).
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "name": "Downtown Branch",
        "branch_code": 10101,
        "location": "Suite 200, City Center",
        "company": 1,
        "company_name": "SecureLife Insurance",
        "user": 2, // ID of the branch admin user
        "user_details": {
            "id": 2,
            "username": "branchadmin1",
            "first_name": "Branch",
            "last_name": "Admin",
            "email": "badmin1@securelife.com",
            // ... other user fields ...
        }
    }
    ```
*   **POST/PUT (Example):**
    ```json
    {
        "name": "Uptown Branch",
        "branch_code": 10102,
        "location": "Uptown Plaza",
        "company": 1,
        "user": 3 // Assign User with ID 3 (must be user_type='branch')
    }
    ```

---

### InsurancePolicy (`/api/insurance-policies/`)

Defines the types of insurance policies offered.

*   **Fields:** `id` (read-only), `name`, `policy_code`, `policy_type` (Choices: "Term", "Endowment"), `base_multiplier` (Decimal), `min_sum_assured` (Decimal), `max_sum_assured` (Decimal), `include_adb`, `include_ptd`, `adb_percentage` (Decimal), `ptd_percentage` (Decimal), `description`, `created_at` (read-only), `gsv_rates` (read-only, nested GSVRate list), `ssv_configs` (read-only, nested SSVConfig list).
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "name": "SecureTerm 20",
        "policy_code": "TERM20",
        "policy_type": "Term",
        "base_multiplier": "1.00",
        "min_sum_assured": "10000.00",
        "max_sum_assured": "500000.00",
        "include_adb": true,
        "include_ptd": false,
        "adb_percentage": "0.10",
        "ptd_percentage": "0.00",
        "description": "A 20-year term life policy with ADB rider.",
        "created_at": "2023-10-26T12:00:00Z",
        "gsv_rates": [ ... ],
        "ssv_configs": [ ... ]
    }
    ```
*   **POST/PUT (Example):**
    ```json
    {
        "name": "SecureEndow 15",
        "policy_code": "ENDOW15",
        "policy_type": "Endowment",
        "base_multiplier": "1.50",
        "min_sum_assured": "5000.00",
        "max_sum_assured": "250000.00",
        "include_adb": true,
        "include_ptd": true,
        "adb_percentage": "0.10",
        "ptd_percentage": "0.15",
        "description": "A 15-year endowment policy."
    }
    ```

---

### GSVRate (`/api/gsv-rates/`)

Guaranteed Surrender Value rates associated with an InsurancePolicy.

*   **Fields:** `id` (read-only), `policy` (ID), `min_year`, `max_year`, `rate` (Decimal).
*   **GET/POST/PUT (Example):**
    ```json
    {
        "id": 1, // Read-only on GET
        "policy": 1, // Link to InsurancePolicy ID 1
        "min_year": 3,
        "max_year": 5,
        "rate": "30.00" // 30%
    }
    ```

---

### SSVConfig (`/api/ssv-configs/`)

Special Surrender Value configurations for an InsurancePolicy.

*   **Fields:** `id` (read-only), `policy` (ID), `min_year`, `max_year`, `ssv_factor` (Decimal), `eligibility_years`, `custom_condition`.
*   **GET/POST/PUT (Example):**
    ```json
    {
        "id": 1, // Read-only on GET
        "policy": 2, // Link to InsurancePolicy ID 2
        "min_year": 5,
        "max_year": 10,
        "ssv_factor": "80.00", // 80%
        "eligibility_years": 5,
        "custom_condition": "Only applicable if premiums fully paid."
    }
    ```

---

### AgentApplication (`/api/agent-applications/`)

Applications submitted by potential agents.

*   **Fields:** `id` (read-only), `branch` (ID), `branch_name` (read-only), `first_name`, `last_name`, `father_name`, `mother_name`, `grand_father_name`, `grand_mother_name`, `date_of_birth`, `gender`, `email`, `phone_number`, `address`, `resume` (file), `citizenship_front` (image), `citizenship_back` (image), `license_front` (image), `license_back` (image), `pp_photo` (image), `license_number`, `license_issue_date`, `license_expiry_date`, `license_type`, `license_issue_district`, `license_issue_zone`, `license_issue_province`, `license_issue_country`, `status` (Choices: "Pending", "Approved", "Rejected"), `created_at` (read-only).
*   **GET (Example):** (File/Image fields show URLs)
    ```json
    {
        "id": 1,
        "branch": 1,
        "branch_name": "Downtown Branch",
        "first_name": "Potential",
        "last_name": "Agent",
        // ... other fields ...
        "email": "p.agent@email.com",
        "phone_number": "1122334455",
        "resume": "/media/agent_application/resume.pdf",
        "pp_photo": "/media/agent_application/photo.jpg",
        "status": "Pending",
        "created_at": "2023-10-27"
    }
    ```
*   **POST/PUT (Example):** (Files/Images handled via multipart/form-data)
    ```json
    {
        "branch": 1,
        "first_name": "Potential",
        "last_name": "Agent",
        "email": "p.agent@email.com",
        "phone_number": "1122334455",
         // ... other required fields ...
        "status": "Pending" // Can be updated by Admin/Branch Admin
    }
    ```

---

### SalesAgent (`/api/sales-agents/`)

Represents approved sales agents linked to a branch and an application.

*   **Fields:** `id` (read-only), `branch` (ID), `branch_name` (read-only), `application` (ID), `agent_name` (read-only), `agent_code`, `is_active`, `joining_date`, `commission_rate` (Decimal), `total_policies_sold` (read-only), `total_premium_collected` (read-only), `last_policy_date` (read-only), `termination_date`, `termination_reason`, `status` (Choices: "ACTIVE", "TERMINATED", "ON_LEAVE").
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "branch": 1,
        "branch_name": "Downtown Branch",
        "application": 1, // Link to AgentApplication ID 1
        "agent_name": "Potential Agent", // Derived from application
        "agent_code": "AG1001",
        "is_active": true,
        "joining_date": "2023-01-15",
        "commission_rate": "5.00",
        "total_policies_sold": 15,
        "total_premium_collected": "25000.00",
        "last_policy_date": "2023-10-20",
        "termination_date": null,
        "termination_reason": null,
        "status": "ACTIVE"
    }
    ```
*   **POST/PUT (Example):**
    ```json
    {
        "branch": 1,
        "application": 1, // Link to an *approved* application
        "agent_code": "AG1002",
        "is_active": true,
        "joining_date": "2023-11-01",
        "commission_rate": "5.50",
        "status": "ACTIVE"
    }
    ```

---

### DurationFactor (`/api/duration-factors/`)

Factors used in premium calculation based on policy duration and type.

*   **Fields:** `id` (read-only), `min_duration`, `max_duration`, `factor` (Decimal), `policy_type` (Choices: "Term", "Endowment").
*   **GET/POST/PUT (Example):**
    ```json
    {
        "id": 1, // Read-only on GET
        "min_duration": 11,
        "max_duration": 15,
        "factor": "1.20",
        "policy_type": "Endowment"
    }
    ```

---

### Customer (`/api/customers/`)

Represents registered customers.

*   **Fields:** `id` (read-only), `first_name`, `middle_name`, `last_name`, `email`, `phone_number`, `address`, `profile_picture` (image), `gender` (Choices: "M", "F", "O"), `user_details` (read-only, nested User object), `password` (write-only), `created_at` (read-only), `updated_at` (read-only).
*   **Note:** Creating a customer automatically creates a linked `User` account with `user_type='customer'` and a username derived from the email prefix.
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "first_name": "John",
        "middle_name": null,
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890",
        "address": "123 Main St",
        "profile_picture": "/media/profile_pictures/john.jpg",
        "gender": "M",
        "user_details": {
            "id": 5,
            "username": "johndoe",
            "email": "john.doe@example.com",
            // ... other user fields ...
        },
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:15:00Z"
    }
    ```
*   **POST (Example):** (Profile picture handled via multipart/form-data)
    ```json
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@sample.org", // Must be unique
        "password": "her_secret_password", // Optional, sets password for the auto-created user
        "phone_number": "5551234567",
        "address": "789 Pine Ln",
        "gender": "F"
    }
    ```
*   **PUT/PATCH (Example):**
    ```json
    {
        "phone_number": "5559876543",
        "address": "101 New Address Blvd",
        "password": "new_secure_password" // Optional, updates linked user's password
    }
    ```

---

### KYC (`/api/kyc/`)

Know Your Customer verification details linked to a Customer.

*   **Fields:** `id` (read-only), `customer` (ID), `customer_name` (read-only), `document_type`, `document_number`, `document_front` (image), `document_back` (image), `pan_number`, `pan_front` (image), `pan_back` (image), `pp_photo` (image), `province`, `district`, `municipality`, `ward`, `nearest_hospital`, `natural_hazard_exposure` (Choices: "Low", "Moderate", "High"), `status` (Choices: "Pending", "Approved", "Rejected").
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "customer": 1,
        "customer_name": "John Doe",
        "document_type": "Citizenship",
        "document_number": "123-456-789",
        "document_front": "/media/customer_kyc/cz_front.jpg",
        "document_back": "/media/customer_kyc/cz_back.jpg",
        "pan_number": "ABCDE1234F",
        "pan_front": "/media/customer_kyc/pan_front.jpg",
        "pan_back": null,
        "pp_photo": "/media/customer_kyc/pp.jpg",
        "province": "Bagmati",
        "district": "Kathmandu",
        "municipality": "KMC",
        "ward": "16",
        "nearest_hospital": "General Hospital",
        "natural_hazard_exposure": "Low",
        "status": "Approved"
    }
    ```
*   **POST/PUT (Example):** (Images handled via multipart/form-data)
    ```json
    {
        "customer": 1,
        "document_type": "Passport",
        "document_number": "P1234567",
        "pan_number": "FGHIJ5678K",
        "province": "Gandaki",
        "district": "Kaski",
        "municipality": "Pokhara Metro",
        "ward": "10",
        "status": "Pending" // Updated by Admin/Agent
    }
    ```

---

### PolicyHolder (`/api/policy-holders/`)

Represents a customer's insurance policy instance.

*   **Fields:** Too many to list concisely. Includes links to `company`, `branch`, `customer`, `agent`, `policy`. Contains details like `policy_number`, `duration_years`, `sum_assured`, `date_of_birth`, `age` (read-only), contacts, nominee details (including images), health info, occupation link, financial details, payment interval, risk category, `status`, `payment_status`, `start_date`, `maturity_date` (read-only). Includes `depth = 1` in serializer, meaning related objects (like Customer, Policy, Agent) will be nested one level deep in GET responses.
*   **GET (Example - Partial):**
    ```json
    {
        "id": 1,
        "company": { ... company details ... },
        "branch": { ... branch details ... },
        "customer": { ... customer details ... },
        "policy_number": "10110101TERM200001",
        "agent": { ... agent details ... },
        "policy": { ... insurance policy details ... },
        "duration_years": 20,
        "sum_assured": "100000.00",
        "date_of_birth": "1990-05-15",
        "age": 33, // Calculated
        "phone_number": "1234567890",
        "nominee_name": "Jane Doe",
        // ... many other fields ...
        "status": "Active",
        "payment_status": "Paid",
        "start_date": "2023-01-01",
        "maturity_date": "2043-01-01" // Calculated
    }
    ```
*   **POST/PUT (Example - Partial):** (Nominee images handled via multipart/form-data)
    ```json
    {
        "company": 1,
        "branch": 1,
        "customer": 1, // Customer must have approved KYC
        "agent": 1,    // Optional
        "policy": 1,   // Link to InsurancePolicy
        "duration_years": 15,
        "sum_assured": "75000.00",
        "date_of_birth": "1985-03-20",
        "phone_number": "5556667777",
        "nominee_name": "Spouse Name",
        "nominee_relation": "Spouse",
        "occupation": 2, // Link to Occupation
        "payment_interval": "annual",
        "status": "Active" // Set to Active to generate policy number
    }
    ```

---

### BonusRate (`/api/bonus-rates/`)

Defines bonus rates per thousand sum assured based on policy and duration range.

*   **Fields:** `id` (read-only), `year`, `policy` (ID), `policy_name` (read-only), `min_year`, `max_year`, `bonus_per_thousand` (Decimal).
*   **GET/POST/PUT (Example):**
    ```json
    {
        "id": 1, // Read-only on GET
        "year": 2023,
        "policy": 2, // Link to InsurancePolicy ID 2
        "policy_name": "SecureEndow 15", // Read-only on GET
        "min_year": 6,
        "max_year": 10,
        "bonus_per_thousand": "50.00"
    }
    ```

---

### Bonus (`/api/bonuses/`)

Tracks accrued bonuses for a customer.

*   **Fields:** `id` (read-only), `customer` (ID), `policy_holder_number` (read-only), `bonus_type` (Choices: "SI", "CI"), `accrued_amount` (read-only, Decimal), `start_date`.
*   **Note:** `accrued_amount` is calculated automatically on save based on the linked policy holder's details and `BonusRate`.
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "customer": 1,
        "policy_holder_number": "10110101TERM200001",
        "bonus_type": "SI",
        "accrued_amount": "5000.00", // Calculated
        "start_date": "2024-01-01"
    }
    ```
*   **POST/PUT (Example):**
    ```json
    {
        "customer": 1,
        "bonus_type": "SI",
        "start_date": "2024-01-01"
        // accrued_amount is calculated by the server
    }
    ```

---

### ClaimRequest (`/api/claim-requests/`)

Requests submitted by policyholders for claims.

*   **Fields:** `id` (read-only), `policy_holder` (ID), `policy_holder_number` (read-only), `customer_name` (read-only), `branch` (ID), `branch_name` (read-only), `claim_date` (read-only), `status` (Choices: "Pending", "Approved", "Rejected"), `reason`, `other_reason`, `documents` (file), `claim_amount` (read-only, Decimal).
*   **Note:** `branch` is often derived from `policy_holder` on create. `claim_amount` calculated on save (e.g., 60% of sum assured).
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "policy_holder": 1,
        "policy_holder_number": "10110101TERM200001",
        "customer_name": "John Doe",
        "branch": 1,
        "branch_name": "Downtown Branch",
        "claim_date": "2023-10-27",
        "status": "Pending",
        "reason": "Maturity",
        "other_reason": null,
        "documents": "/media/claims/doc1.pdf",
        "claim_amount": "60000.00" // Calculated
    }
    ```
*   **POST/PUT (Example):** (Document handled via multipart/form-data)
    ```json
    {
        "policy_holder": 1,
        // "branch": 1, // Often automatically set
        "status": "Pending", // Updated by Admin/Branch Admin during processing
        "reason": "Death Claim",
        "other_reason": "Details about the event."
    }
    ```

---

### ClaimProcessing (`/api/claim-processing/`)

Tracks the processing status of a claim request.

*   **Fields:** `id` (read-only), `claim_request` (ID), `claim_number` (read-only), `branch` (ID), `branch_name` (read-only), `company` (ID), `company_name` (read-only), `processing_status` (Choices: "Processing", "Approved", "Rejected"), `remarks`, `processed_at` (read-only).
*   **Note:** `branch` and `company` are often derived from `claim_request` on create. Use the `finalize` custom action to update status and trigger payment processing if approved.
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "claim_request": 1,
        "claim_number": "Claim #1",
        "branch": 1,
        "branch_name": "Downtown Branch",
        "company": 1,
        "company_name": "SecureLife Insurance",
        "processing_status": "Processing",
        "remarks": "Awaiting final documents.",
        "processed_at": "2023-10-27T14:00:00Z"
    }
    ```
*   **POST/PUT (Example):**
    ```json
    {
        "claim_request": 1,
        // "branch": 1, // Auto-set
        // "company": 1, // Auto-set
        "processing_status": "Processing", // Change to Approved/Rejected via finalize action or direct PUT
        "remarks": "Documents reviewed, pending verification."
    }
    ```

---

### PaymentProcessing (`/api/payment-processing/`)

Tracks the final payout details for an approved claim.

*   **Fields:** `id` (read-only), `claim_request` (ID), `claim_number` (read-only), `branch` (ID), `branch_name` (read-only), `company` (ID), `company_name` (read-only), `processing_status` (Choices: "Pending", "Completed", "Failed"), `amount_paid` (read-only, Decimal), `payment_date` (read-only), `payment_reference`.
*   **Note:** `amount_paid` is calculated automatically (Sum Assured + Bonuses - Loans). `branch` and `company` derived from claim. Created automatically when `ClaimProcessing` is finalized as "Approved".
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "claim_request": 1,
        "claim_number": "Claim #1",
        "branch": 1,
        "branch_name": "Downtown Branch",
        "company": 1,
        "company_name": "SecureLife Insurance",
        "processing_status": "Pending", // Updates to Completed/Failed
        "amount_paid": "105000.00", // Calculated
        "payment_date": "2023-10-28T09:00:00Z",
        "payment_reference": null
    }
    ```
*   **POST/PUT (Example):** (Typically only update status/reference)
    ```json
    {
        "claim_request": 1, // Must link to an approved ClaimRequest
        "processing_status": "Completed",
        "payment_reference": "TXN12345ABC"
    }
    ```

---

### Underwriting (`/api/underwriting/`)

Risk assessment for a policyholder.

*   **Fields:** `id` (read-only), `policy_holder` (ID), `policy_holder_number` (read-only), `customer_name` (read-only), `risk_assessment_score` (Decimal), `risk_category` (Choices: "Low", "Moderate", "High"), `manual_override`, `remarks`, `last_updated_by` (read-only), `last_updated_at` (read-only).
*   **Note:** Score and category are calculated automatically unless `manual_override` is true.
*   **GET/POST/PUT (Example):**
    ```json
    {
        "id": 1, // Read-only on GET
        "policy_holder": 1,
        "policy_holder_number": "10110101TERM200001", // Read-only on GET
        "customer_name": "John Doe", // Read-only on GET
        "risk_assessment_score": "35.00", // Calculated or Manual
        "risk_category": "Low", // Calculated or Manual
        "manual_override": false,
        "remarks": "Standard risk profile.",
        "last_updated_by": "System", // Read-only on GET
        "last_updated_at": "2023-10-27T15:00:00Z" // Read-only on GET
    }
    ```

---

### PremiumPayment (`/api/premium-payments/`)

Tracks premium payments for a policyholder.

*   **Fields:** `id` (read-only), `policy_holder` (ID), `policy_holder_number` (read-only), `customer_name` (read-only), `annual_premium` (read-only), `interval_payment` (read-only), `total_paid` (read-only), `paid_amount` (write-only, amount being paid *now*), `next_payment_date` (read-only), `fine_due` (Decimal), `total_premium` (read-only), `remaining_premium` (read-only), `gsv_value` (read-only), `ssv_value` (read-only), `payment_status` (read-only).
*   **Note:** Many fields are calculated automatically on save based on the policy and payments made. Provide `paid_amount` to record a new payment.
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "policy_holder": 1,
        "policy_holder_number": "10110101TERM200001",
        "customer_name": "John Doe",
        "annual_premium": "1200.00",
        "interval_payment": "1200.00", // Assumes annual interval
        "total_paid": "1200.00",
        "next_payment_date": "2024-01-01",
        "fine_due": "0.00",
        "total_premium": "24000.00", // annual_premium * duration
        "remaining_premium": "22800.00",
        "gsv_value": "300.00", // Example calculated GSV
        "ssv_value": "0.00", // Example calculated SSV
        "payment_status": "Partially Paid"
    }
    ```
*   **POST/PUT (Example):** (Use PATCH for adding payment)
    ```json
    // To create the initial record (usually done automatically with PolicyHolder?)
    {
        "policy_holder": 1
    }
    // To record a payment (PATCH is better)
    {
        "paid_amount": "1200.00", // Amount being paid now
        "fine_due": "50.00" // If applicable, add fine to payment
    }
    ```

---

### AgentReport (`/api/agent-reports/`)

Summary report of an agent's performance.

*   **Fields:** `id` (read-only), `agent` (ID), `agent_name` (read-only), `branch` (ID), `branch_name` (read-only), `report_date`, `reporting_period`, `policies_sold`, `total_premium` (Decimal), `commission_earned` (Decimal), `target_achievement` (Decimal), `renewal_rate` (Decimal), `customer_retention` (Decimal).
*   **GET/POST/PUT (Example):**
    ```json
    {
        "id": 1, // Read-only on GET
        "agent": 1,
        "agent_name": "Potential Agent", // Read-only on GET
        "branch": 1,
        "branch_name": "Downtown Branch", // Read-only on GET
        "report_date": "2023-10-01",
        "reporting_period": "Q3 2023",
        "policies_sold": 5,
        "total_premium": "8500.00",
        "commission_earned": "425.00",
        "target_achievement": "95.50",
        "renewal_rate": "88.00",
        "customer_retention": "92.00"
    }
    ```

---

### Loan (`/api/loans/`)

Represents loans taken out against a policy.

*   **Fields:** `id` (read-only), `policy_holder` (ID), `policy_holder_number` (read-only), `customer_name` (read-only), `loan_amount` (Decimal), `interest_rate` (Decimal), `remaining_balance` (read-only, Decimal), `accrued_interest` (read-only, Decimal), `loan_status` (Choices: "Active", "Paid"), `last_interest_date` (read-only), `created_at` (read-only), `updated_at` (read-only).
*   **Note:** Validation ensures `loan_amount` doesn't exceed 90% of GSV. Use `accrue_interest` custom action to update interest.
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "policy_holder": 1,
        "policy_holder_number": "10110101TERM200001",
        "customer_name": "John Doe",
        "loan_amount": "500.00",
        "interest_rate": "8.00",
        "remaining_balance": "500.00",
        "accrued_interest": "10.50",
        "loan_status": "Active",
        "last_interest_date": "2023-10-27",
        "created_at": "2023-10-01",
        "updated_at": "2023-10-27"
    }
    ```
*   **POST/PUT (Example):**
    ```json
    {
        "policy_holder": 1,
        "loan_amount": "500.00", // Must be <= 90% of policy GSV
        "interest_rate": "8.00"
        // status defaults to Active
    }
    ```

---

### LoanRepayment (`/api/loan-repayments/`)

Tracks repayments made towards a loan.

*   **Fields:** `id` (read-only), `loan` (ID), `loan_id` (read-only), `policy_holder_number` (read-only), `repayment_date` (read-only), `amount` (Decimal), `repayment_type` (Choices: "Principal", "Interest", "Both"), `remaining_loan_balance` (read-only, Decimal).
*   **Note:** Processing (updating loan balance/interest) happens automatically on save.
*   **GET (Example):**
    ```json
    {
        "id": 1,
        "loan": 1,
        "loan_id": 1,
        "policy_holder_number": "10110101TERM200001",
        "repayment_date": "2023-11-01",
        "amount": "50.00",
        "repayment_type": "Both",
        "remaining_loan_balance": "460.50" // Example: 500 principal + 10.50 interest - 50 payment
    }
    ```
*   **POST (Example):**
    ```json
    {
        "loan": 1,
        "amount": "50.00",
        "repayment_type": "Both" // Or Principal/Interest
    }
    ```

---

## Permissions Overview

*   **Authentication:** Most endpoints require authentication via the Token mechanism described above. Exceptions are Customer registration (`POST /api/customers/`) and Agent application (`POST /api/agent-applications/`).
*   **Admins (Superusers/Staff):** Have full access to all endpoints and operations.
*   **Configuration Models:** Endpoints like `/api/occupations/`, `/api/mortality-rates/`, `/api/companies/`, `/api/insurance-policies/`, `/api/gsv-rates/`, `/api/ssv-configs/`, `/api/duration-factors/`, `/api/bonus-rates/` are generally restricted to Admins.
*   **Branch Admins (`user_type='branch'`):** Can typically manage resources within their assigned branch (Agents, PolicyHolders, Claims, Payments, Underwriting, Reports). They can view/manage agent applications for their branch.
*   **Agents (`user_type='agent'`):** Can typically view/manage customers, policies, claims, loans, etc., that are directly assigned to them. They can view their own reports (if implemented in `get_queryset`).
*   **Customers (`user_type='customer'`):** Can typically view/manage their own profile (`/api/users/me/` - if set up, or filtered `/api/users/{id}/`), their customer details, KYC, policies, bonuses, claims, loans, and premium payments. They can create claim requests and loan repayments for their policies/loans.
*   **Ownership:** Permissions like `IsOwnerOrAdmin` and `IsOwnerOrAdminOrAgent` restrict updates/deletes to the record's owner (linked user) or an admin/related agent.

Refer to `insurance/views.py` (specifically `get_permissions` and `get_queryset` methods in ViewSets) and `insurance/permissions.py` for the precise permission logic applied to each endpoint and action.
