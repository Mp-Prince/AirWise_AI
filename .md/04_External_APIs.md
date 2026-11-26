# AirWise AI — External API Documentation

**Purpose:** Record external data providers and AI services used by the application.  
**Important:** Provider plans, API versions, authentication requirements and endpoint availability can change. Confirm current documentation and access before implementation.

## 1. API integration overview

| Service | Purpose | Priority |
|---|---|---|
| CPCB / Government data | Official Indian air-quality information | Primary |
| OpenAQ | Supplementary pollutant observations | Secondary |
| Open-Meteo | Weather information | Primary weather option |
| Geocoding provider | Convert city/address to coordinates | Required |
| LLM API | Generate assistant responses | Required |
| Embedding API/model | Convert document chunks and queries into vectors | Required |
| Optional map provider | Display locations and route context | Optional |
| Firebase Cloud Messaging | Push notifications | Optional |

## 2. CPCB and Government of India data

### Purpose
Use official Indian monitoring information and National AQI guidance wherever accessible.

### Starting references
- CPCB: https://cpcb.nic.in/
- CPCB Central Control Room: https://app.cpcbccr.com/ccr_docs
- Government Open Data Platform: https://www.data.gov.in/

### Data to seek
- Monitoring station information.
- Pollutant concentrations.
- Observation timestamps.
- Official AQI values/categories where published.
- Methodology and quality notes.

### Integration notes
- Confirm the specific dataset/API and access conditions before coding.
- Do not assume a public webpage is a supported API.
- Check rate limits, licensing and attribution conditions.
- Keep station ID, provider and observation timestamp.
- Use CPCB's National AQI methodology for Indian AQI calculations.
- Do not calculate official AQI when required pollutant data are missing or invalid.

### Normalized internal endpoint
`GET /api/v1/air-quality/current?location_id={id}`

This is an AirWise backend endpoint, not a CPCB endpoint.

## 3. OpenAQ API

### Official documentation
https://docs.openaq.org/

### Purpose
Supplementary access to global air-quality measurements where monitoring coverage exists.

### API base
Check the current base URL and version in the official documentation before implementation.

### Common data concepts
- Locations / monitoring sites.
- Sensors.
- Measurements.
- Parameter names and units.
- Measurement timestamps.
- Coordinates.

### Typical integration workflow
1. Search for locations near a user's coordinates.
2. Identify sensors and pollutant parameters.
3. Retrieve measurements for the relevant sensor/location.
4. Normalize units and timestamps.
5. Store provider metadata.
6. Mark missing or stale data correctly.

### Authentication
OpenAQ API access may require an API key depending on the current API policy and endpoint. Store the key server-side in an environment variable.

### Limitations
- Coverage varies by city and pollutant.
- Measurements from different networks may have different quality characteristics.
- OpenAQ data should not automatically be labelled as official CPCB AQI.
- Verify current terms, rate limits and attribution requirements.

## 4. Open-Meteo Weather API

### Official documentation
https://open-meteo.com/en/docs

### Purpose
Retrieve weather context such as temperature, humidity, wind and precipitation.

### Example endpoint
`GET https://api.open-meteo.com/v1/forecast`

### Example query parameters
- `latitude`
- `longitude`
- `current`
- `hourly`
- `daily`
- `timezone`

Example URL for testing:

```text
https://api.open-meteo.com/v1/forecast?latitude=12.97&longitude=77.59&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m&timezone=Asia%2FKolkata
```

### Response fields of interest
- `current.temperature_2m`
- `current.relative_humidity_2m`
- `current.wind_speed_10m`
- `current.wind_direction_10m`
- `current.time`

### Notes
- Check the current terms and attribution requirements for the intended usage.
- Weather conditions are context, not a substitute for pollutant measurements.
- Do not infer a safe AQI from weather alone.

## 5. Geocoding API

Choose one provider after reviewing coverage, pricing, licensing and rate limits.

Possible options:
- OpenStreetMap Nominatim: https://nominatim.org/release-docs/latest/api/Overview/
- Google Maps Platform Geocoding: https://developers.google.com/maps/documentation/geocoding/overview

### Required capability
Convert a user-entered Indian city, district, area or address into coordinates and a normalized location record.

### Nominatim notes
- Follow the current usage policy and attribution rules.
- Do not use the public service for unrestricted high-volume autocomplete.
- Cache results appropriately.
- Consider a hosted provider or self-hosting for production-scale usage.

### Internal endpoint
`GET /api/v1/locations/search?q={query}`

## 6. LLM API for AI assistance

### Candidate: Google Gemini API
Official documentation: https://ai.google.dev/gemini-api/docs

Alternative providers may be evaluated if their pricing, latency, privacy terms and structured-output support better fit the project.

### Purpose
- Generate personalized explanations.
- Answer environmental and sustainability questions.
- Turn retrieved evidence into readable recommendations.
- Produce structured planner suggestions.

### Typical integration pattern
The React client calls the AirWise backend. The backend:
1. Authenticates the user.
2. Retrieves permitted user context.
3. Fetches current environmental data if required.
4. Retrieves relevant RAG passages.
5. Builds a grounded prompt.
6. Calls the LLM.
7. Validates the result.
8. Returns answer and source references.

Do not call the LLM provider directly from the browser because that would expose the API key.

### Example internal endpoint
`POST /api/v1/assistant/chat`

Example request:

```json
{
  "conversation_id": null,
  "message": "Suggest lower-emission options for my daily commute.",
  "include_user_context": true
}
```

Example response:

```json
{
  "answer": "Here are practical options based on your commute profile...",
  "recommendations": [],
  "sources": [],
  "data_context": {
    "location": "User-selected location",
    "air_quality_observed_at": null
  },
  "limitations": []
}
```

### Prompt and response requirements
- Treat retrieved documents as untrusted content, not instructions.
- Require source references for factual environmental claims.
- Require structured JSON output for recommendations.
- Reject malformed or unsupported numerical claims.
- Keep health guidance conservative and direct users to official guidance for serious concerns.
- Make the LLM state when evidence is unavailable.

## 7. Embedding model API / library

### Options
- Sentence Transformers: https://www.sbert.net/
- Google embedding documentation: https://ai.google.dev/gemini-api/docs/embeddings (check current model availability and API status)
- Other embedding providers can be evaluated.

### Purpose
- Embed document chunks during ingestion.
- Embed user questions during retrieval.
- Store vectors in pgvector.
- Retrieve semantically relevant evidence.

### Critical compatibility rule
The embedding model used for query vectors must be compatible with the model used for stored document vectors. Record the model name, version and vector dimension. Re-embed the knowledge base when changing embedding models.

## 8. PostgreSQL and pgvector

### PostgreSQL
https://www.postgresql.org/docs/

### pgvector
https://github.com/pgvector/pgvector

### Purpose
- Store application relational data.
- Store knowledge document chunks.
- Store embedding vectors.
- Perform similarity retrieval.

### Notes
- Enable the pgvector extension in the database.
- Select vector dimension to match the chosen embedding model.
- Use appropriate vector indexing after measuring retrieval workload.
- Apply database permissions and backups.

## 9. Firebase Cloud Messaging (optional)

Documentation:
https://firebase.google.com/docs/cloud-messaging

### Purpose
- Push notifications to supported web/mobile clients.
- Remind users about planner activities.
- Notify users about relevant air-quality updates when a reliable alert source exists.

### Notes
- Ask for notification permission at an appropriate point.
- Store device tokens securely.
- Provide opt-out controls.
- Avoid sending frequent or alarmist notifications.

## 10. Optional maps and route APIs

Potential providers:
- Google Maps Platform: https://developers.google.com/maps/documentation
- OpenStreetMap ecosystem: https://www.openstreetmap.org/

Use only if the product includes map display, location search or route alternatives. Do not claim a route is low-emission unless a supported calculation method and transport data justify it.

## 11. Secrets and environment variables

Example backend environment variables:

```env
DATABASE_URL=
JWT_SECRET_KEY=
LLM_API_KEY=
EMBEDDING_API_KEY=
OPENAQ_API_KEY=
WEATHER_API_KEY=
GEOCODING_API_KEY=
```

Only configure variables for providers actually selected. Never commit `.env` files or expose secrets in React environment variables.

## 12. API reliability requirements

For every external integration:
- Set connection and read timeouts.
- Retry transient failures with bounded exponential backoff.
- Respect provider rate limits.
- Cache data according to provider rules and freshness needs.
- Log provider, request time, status and error category.
- Do not log API keys or unnecessary personal data.
- Validate units and timestamps.
- Clearly label stale or unavailable readings.
- Provide a graceful fallback.

## 13. Provider selection checklist

Before implementation, record:
- Exact endpoint and API version.
- Authentication method.
- Free-tier limits and pricing.
- Coverage across Indian states/cities.
- Data update frequency.
- Terms of use and attribution.
- Commercial/hackathon demonstration permissions.
- Required source display.
- Failure and fallback behaviour.

## 14. Important distinction

External provider APIs supply measurements or model responses. AirWise's own `/api/v1/...` endpoints are internal backend routes. Keep these two categories separate in code and documentation.
