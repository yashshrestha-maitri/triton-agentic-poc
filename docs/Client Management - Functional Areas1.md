Client Management - Functional Areas1. Client Directory & Search
View all active clients in a searchable, sortable table
Display client name, URL, ROI model types, status, creation date, and creator
Search/filter clients by name
Toggle visibility to show/hide archived or inactive clients
Client status states: Researching, Ready for Review, Active
2. Client Profile Management
Create New Client
Enter client name and website URL
Name and URL validation
Optional: Invite client administrator via email during creation
Edit Client Information
We’ll need an Edit Client view at some point that allows the user to edit the name, update the branding and maybe change the admin
Delete Client
Remove client and all associated data
Confirmation dialog with warning
3. ROI Model Management

This is a new screen and most notably introduces the content of a client having multiple ROI Models.
ROI Model List View
View all ROI models for a specific client
Display model name, status, ROI type classification, and description
Model status indicators: Ready, Updating, Needs Review
Add ROI Model
This configuration is similar to the old screen that allows a user to upload the collateral, enter details, and name their model.
This screen will submit to the research agent and it will use a series of two prompts to determine the ROI Type and then with the type in hand, determine and build the ROI Model.   This is significantly built out in repo mare-triton-research-prompts.   You will find all the current demo clients, their collateral, the prompts, and the results here.
In the mockup we have some dialogs that describe what is happening.  These do not need to exist in the true app…you can simply return the user to the model screen.   They should see their new model in a status of “Updating” or something like that….  
Key note…there is a model schema for both response JSON for the type and model.   Jeff is working on cleaning this up but bottom line there are prompts, you give them data to help, you get data back, it must go into a JSON format (the prompt has this) and you do need to validate that the JSON is formatted correctly.   This should be similar to the research agent structure discussed to date.
Delete ROI Model
Remove specific ROI model
Confirmation with warning about permanent deletion
4. ROI Model Detail & Configuration

These are the first tabs in the drill down on the model from the list.  The purpose of this screen is for Client admins to review and potentially modify the ROI model details.   They can view how demo data looks for their model in the ROI Summary and also provide Feedback to the Research Agent to affect change in the ROI Model.

The first 2-3 tabs on the ROI model vary from ROI Type to Type.  They allow the Client Admin to edit the properties of the model JSON that drive the ROI Calculations and other properties.  The Feedback mechanic (which will likely follow later) will allow for the same.

   Model Overview
View model metadata (type, vendor, solution type, source documents)
ROI Calculation
Derived calculation methodology
Configure savings components and categories
Set baseline metrics and impact calculationsl8ll
Edit calculation parameters with real-time validation
Population Identification
Define inclusion criteria (diagnosis codes, procedure codes, conditions)
Define exclusion criteria
Add, edit, or remove criteria
View code sources and episode relationships
Episode Definitions (for episode-based models)
Configure episode types and grouping methodology
Edit episode parameters
Define episode windows and attribution rules
Model Type-Specific Configurations
Edit Categories (payment integrity models)
Low-Value Services (utilization management)
Program Definition (medical management programs)
Optimization Strategies (various model types)
Pricing Analysis, Site Analysis, Steerage Analysis
OON/Prior Auth Analysis
Leakage Analysis
Device/Supply Chain Analysis
Incentive/Rebate Analysis
Configurable Parameters
Adjust model-specific parameters
Set thresholds and validation rules
Configure assumptions and confidence factors
Change Management
Track unsaved changes across all model components
Save all changes at once or discard
Visual indicators for modified sections
5. ROI Model Visualization & Summary

These are the last two tabs currently.    The summary dashboard does NOT change from ROI Model to ROI Model – regardless of ROI Type.   This is by design.
ROI Summary Dashboard
Graphical visualization of ROI components
Savings breakdown by category
Population funnel visualization
Impact timeline and projections
Model Feedback
Provide feedback on model accuracy
Flag issues or suggest improvements
Allow Client Approval
6. Prospect Flow Change

As noted in the demo the Prospect Flow changes and the current ROI and Value Props go away in favor of showing the ROI Summary.    OPEN QUESTION:  Clients can have more than one ROI model…we might need to consider this and when a Prospect is added we may have to have a model selection available if (and only if) more than one model is detected for the Client.   Then the ROI Summary that shows will be the one associated to that model.
