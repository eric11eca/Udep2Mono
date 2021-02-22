var term_font = "";
var nonterm_font = "";
let color = true,
  term_lines = true,
  font_size = 14,
  vert_space = 50,
  hor_space = 30;

term_font = term_font + font_size + "pt";
nonterm_font = nonterm_font + font_size + "pt ";
term_font = term_font + 'sans-serif';
nonterm_font = nonterm_font + 'sans-serif';


function dosanitize(widget) {
  var data = window.event.clipboardData.getData('text');
  widget.value += sanitize(data);
  window.event.preventDefault();
  return false;
}

function sanitize(x) {
  x = x.replace(/\u00AC/gi, "~");
  x = x.replace(/\u2227/gi, "&");
  x = x.replace(/\u2228/gi, "|");
  x = x.replace(/\u21D2/gi, "=>");
  x = x.replace(/\u21D4/gi, "<=>");
  x = x.replace(/\u2200/gi, "A");
  x = x.replace(/\u2203/gi, "E");
  x = x.replace(/\./gi, ":");
  return x.replace(/[^a-z_0-9~&|=>:-\s\x28\x29\,{}]/gi, "");
}

let notebook = document.querySelector(".notebook");
let global_index = 1;

document.addEventListener('input', function (event) {
  if (event.target.tagName.toLowerCase() !== 'textarea') return;
  autoExpand(event.target);
}, false);

var autoExpand = function (field) {
  field.style.height = 'inherit';
  var computed = window.getComputedStyle(field);
  var height = parseInt(computed.getPropertyValue('border-top-width'), 10) +
    parseInt(computed.getPropertyValue('padding-top'), 10) +
    field.scrollHeight +
    parseInt(computed.getPropertyValue('padding-bottom'), 10) +
    parseInt(computed.getPropertyValue('border-bottom-width'), 10);
  field.style.height = height + 'px';
};

function addNewCell(button_id) {
  var index = button_id[button_id.length - 1];
  global_index += 1;
  var newButtonBarID = 'buttonbar' + global_index.toString();
  var newInputID = 'input' + global_index.toString();
  var newAddID = 'add' + global_index.toString();
  var newCompileID = 'compile' + global_index.toString();
  var newCell = '<p><textarea id="newInputID" onkeyup="compileKeyDown(event, this.id)"></textarea></p>' +
    '<div class="conclusion" id="newButtonBarID"> <div class="addNew">' +
    '<button class="add btn btn-light" id="newAddID" type="button" onclick="addNewCell(this.id)">' +
    '<ion-icon name="add-outline"></ion-icon></button>' +
    '<button class="compile btn btn-light" id="newCompileID" type="button" onclick="compileLogic(this.id)">' +
    '<ion-icon name="caret-forward-outline"> </ion-icon></button></div>';
  newCell = newCell.replace('newButtonBarID', newButtonBarID);
  newCell = newCell.replace('newInputID', newInputID);
  newCell = newCell.replace('newAddID', newAddID);
  newCell = newCell.replace('newCompileID', newCompileID);
  document.querySelector('#buttonbar' + index).insertAdjacentHTML('afterend', newCell);
}

function compileKeyDown(event, button_id) {
  if (event.keyCode == 13 && event.shiftKey) {
    compileLogic(button_id);
  }
}

function compileLogic(button_id) {
  var index = button_id[button_id.length - 1];
  var premises = document.querySelector('#input' + index).value;
  if (premises == "") {
    return;
  }

  let sentences = premises.split('\n');
  console.log(sentences);

  fetch('/annotate', {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      sentences: sentences
    })
  }).then((response) => {
    if (!response.ok) {
      throw new Error("Unable to get annotations");
    }

    var truth_tables = document.getElementById('truth_tables' + index);
    if (truth_tables != undefined) {
      truth_tables.parentNode.removeChild(truth_tables);
    }

    truth_tables = document.createElement('div');
    truth_tables.classList.add("truth_tables");
    truth_tables.setAttribute('id', 'truth_tables' + index);

    response.text().then(text => {
      let annotations = JSON.parse(text).annotations;
      for (var annotation of annotations) {
        var img = go(annotation[2], font_size, term_font, nonterm_font, vert_space, hor_space, color, term_lines);
        var annotated = document.createElement("h6");
        annotated.innerHTML = annotation[0];
        truth_tables.appendChild(img);
        truth_tables.appendChild(annotated);
      }
      
      document.querySelector('#buttonbar' + index).insertAdjacentHTML('beforeend', outerHTML(truth_tables));
    });

    return result;
  }).catch((err) => {
    console.log(err);
  });
}

function outerHTML(node) {
  var wrapper = document.createElement("div");
  wrapper.appendChild(node);
  return wrapper.innerHTML;
}

function toggleinstructions(toggle) {
  if (toggle.innerHTML == 'Hide Instructions') {
    toggle.innerHTML = 'Show Instructions';
    document.getElementById('instructions').style.display = 'none';
    return true;
  }

  toggle.innerHTML = 'Hide Instructions';
  document.getElementById('instructions').style.display = '';
  return true;
}