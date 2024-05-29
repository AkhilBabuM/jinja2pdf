document.addEventListener("DOMContentLoaded", function () {
  fetch("form_data.json")
    .then((response) => response.json())
    .then((data) => {
      const contentDiv = document.getElementById("content");
      const fieldOrder = data.field_order;
      const fields = data.fields;
      let currentSection = null;
      let currentColumn = null;

      fieldOrder.forEach((fieldname) => {
        const fieldData = fields.find((field) => field.fieldname === fieldname);

        if (!fieldData) return;

        if (fieldData.fieldtype === "Section Break") {
          currentSection = document.createElement("div");
          currentSection.className = "section";
          currentSection.innerHTML = `<h2>${fieldData.label}</h2><br/>`;
          contentDiv.appendChild(currentSection);
          currentColumn = null;
        } else if (fieldData.fieldtype === "Column Break") {
          currentColumn = document.createElement("div");
          currentColumn.className = "column-break";
          currentSection.appendChild(currentColumn);
        } else {
          const fieldElement = document.createElement("div");
          fieldElement.className = "field";
          fieldElement.innerHTML = `<label>${
            fieldData.label
          }</label>: <br/> ${createInputField(fieldData)}`;

          if (currentColumn) {
            currentColumn.appendChild(fieldElement);
          } else if (currentSection) {
            currentSection.appendChild(fieldElement);
          } else {
            contentDiv.appendChild(fieldElement);
          }
        }
      });

      // Populate form with data from another JSON file
      fetch("form_submit_data.json")
        .then((response) => response.json())
        .then((formData) => {
          fieldOrder.forEach((fieldname) => {
            const fieldData = fields.find(
              (field) => field.fieldname === fieldname
            );
            if (fieldData && formData[fieldname]) {
              const inputElement = document.querySelector(
                `[name="${fieldname}"]`
              );
              if (inputElement) {
                inputElement.value = formData[fieldname];
              }
            }
          });
        })
        .catch((error) =>
          console.error("Error loading form data JSON:", error)
        );
    })
    .catch((error) => console.error("Error loading JSON:", error));

  function myCustomFunction() {
    // Perform some task here

    // Set a flag or return a value when the task is done
    return true;
  }

  // Call the custom function
  myCustomFunction();
});

function createInputField(fieldData) {
  let input;
  switch (fieldData.fieldtype) {
    case "Data":
      input = `<input type="text" name="${fieldData.fieldname}" />`;
      break;
    case "Int":
      input = `<input type="number" name="${fieldData.fieldname}" />`;
      break;
    case "Select":
      const options = fieldData.options
        .split("\n")
        .map((option) => `<option value="${option}">${option}</option>`)
        .join("");
      input = `<select name="${fieldData.fieldname}">${options}</select>`;
      break;
    case "Text":
      input = `<textarea name="${fieldData.fieldname}"></textarea>`;
      break;
    default:
      input = `<input type="text" name="${fieldData.fieldname}" />`;
  }
  return input;
}
