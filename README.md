> [!WARNING]
> This app is not ready for production. Large changes should be expected until a 1.0.0 version is released.

### ⛪ Church

A fully open-source church management app built on the [Frappe Framework](https://frappe.io/framework).

![onboarding screenshot](screenshots/Onboarding.png "Onboarding")

### ✨ Features

The following features have been implemented in this app (see the [🗺️ Roadmap](#🗺️-roadmap) below for future plans):

- `Church Person` tracking
  - Define and track `Church Person Relation`ships
    - Define `Church Person Relation Type`s
  - Define & track `Church Person Role`s (i.e. board member, deacon, pastor, etc)
- `Church Family` tracking
  - Track head of household (Set on `Church Person` record)
- Church module desk workspace with guided setup steps
- Event tracking
  - Event types, details, basic attendance tracking & reporting
- Collection/donation tracking
  - Donation entry with collection totals & split check support
  - Bank reconciliation report

### 📥 Installation

To use this app, you must have a working Frappe environment. The easiest way to get a working Frappe environment is to use [Frappe Cloud](https://frappe.io/cloud). For a few dollars per month you can run an instance in the cloud. To self-host an instance on a home pc or server, you can use [frappe-manager](https://github.com/rtcamp/frappe-manager) to quickly setup a local frappe instance. Making a local instance of frappe accessible from outside of your network is currently out of the scope of this project, but with some persistence and some technical expertise, it shouldn't be too difficult.

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app church
```

After the above installation and a WebUI reload, you should see the `Church` app installed when you view `Help > About` in the [Frappe Desk](https://docs.frappe.io/framework/user/en/desk).

### 🗺️ Roadmap

Hopefully this roadmap will help avoid too much scope creep and provide a sense of where this project is headed. The items below are listed in order of current priority.

- Add Onboarding Tours
  - Add 'Tutorial' button to each doctype form
- Ministry tracking
- Fund Tracking
  - Update fund balance after collection submission
- Add standard church website pages:
  - About Us
  - Home/Welcome
  - Missions
  - Beliefs/Statement of Faith
  - Calendar
  - Contact Us
- Collection Improvements
  - Make collections submittable(?)
- Add portal for `Church Person`s
  - Show tracked giving
  - Show tracked attendance
    - Allow updating attendance status(?)
- Event templating/recurrence
  - Templating via `Church Event Type` default values table(?)
- Add table to `Church Family` form to show current members

### 🤝 Contributing

Contributions are very welcome! If you plan any large contributions, please let me know first so we can coordinate and make the chances of a merged pull-request more likely.

- Doctype Naming: I've generally been using a single fieldname for the doctype names when the records in the doctype have low chance of clashing. If there is a higher chance of clashing, I've been using multiple fields in the name along with a `{####}` auto increment. The number of digits in the auto-increment are just sane values that should never be exceeded. I then specify the Title Field in the View Settings, and check the `Show Title in LInk Fields` option. This mostly hides the autonumber name from the user and lets the user only see the not-so-confusing name specified in the `Title Field` (sometimes I create a custom field to concatenate values - since the `Title Field` cannot take multiple fields at once afaik.)

#### Pre-Commit

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/church
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### 🔑 License

MIT
