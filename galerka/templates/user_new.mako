<form method="POST" action="${this.url}">
    <fieldset>
    <ul>
        % for field in this.form:
        <li>
            ${field.label}
            ${field(class_='widget-' + type(field.widget).__name__)}
            <ul class="errors">
                % for error in field.errors:
                    <li>${error}</li>
                % endfor
            </ul>
        </li>
        % endfor
    </ul>
    </fieldset>
    <fieldset class="buttons">
        <button id="submit" type="submit">Založit účet</button>
    </fieldset>
</form>
