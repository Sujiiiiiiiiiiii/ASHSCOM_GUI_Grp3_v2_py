---
name: add-committee-crud-feature
description: Added a CRUD feature for managing committees in the Users tab, inside a scrollable area, in a section labeled 'Add committee'
metadata:
  type: project
---

Added a CRUD (Create, Read, Update, Delete) feature for managing committees in the Users tab. The feature is contained within a LabelFrame labeled 'Add committee' and includes:

- Input field for committee name (required)
- Buttons for adding, updating, and deleting committees
- A Treeview to display the list of committees
- Functionality to load committees from the database and reflect changes in real-time
- Validation to ensure the committee name is provided before saving

The feature uses the existing database connection and creates a 'committees' table if it doesn't exist, with the name field set as NOT NULL to enforce data integrity at the database level.

**How to apply:** This feature can be extended by adding more fields to the committee entity (e.g., description, chairperson, etc.) or changing input types. It is located in the create_users_tab method and helper methods in ashscom_gui.py.

**Related to:** [[add-student-crud-feature]] - Both features are implemented in the Users tab and share similar CRUD patterns.