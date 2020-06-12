package main

import (
	"log"
	"fmt"

	"github.com/singularityhub/containerdb"
)

func main() {

	// Open an in-memory database
        db, err := containerdb.Open(":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	db.Update(func(tx *containerdb.Tx) error {
		{% for filename, metadata in updates.items() %}_, _, err {% if loop.first %}:={% else %}={% endif %} tx.Set(`{{ filename }}`, `{{ metadata }}`, nil)
                {% endfor %}
		return err
	})

	db.View(func(tx *containerdb.Tx) error {
		{% for filename, metadata in updates.items() %}val, err {% if loop.first %}:={% else %}={% endif %} tx.Get("{{ filename }}")
		if err != nil{
			return err
		}
		fmt.Printf("value is %s\n", val)
		{% endfor %}
		return nil
	})

}
