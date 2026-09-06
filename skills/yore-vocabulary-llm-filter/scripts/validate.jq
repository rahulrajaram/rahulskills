# jq -e -s --slurpfile expected expected-terms.json -f validate.jq result.json
# Slurp both files to reject streams containing more than one JSON document.
def nonempty_string: type == "string" and test("\\S");
def unique_terms: length == (unique | length);
def valid_term:
  . as $entry |
  type == "object" and
  keys == ["category", "reason", "term", "verdict"] and
  (.term | nonempty_string) and (.reason | nonempty_string) and
  (.verdict | type == "string") and (.category | type == "string") and
  (["keep", "drop", "review", "artifact"] | index($entry.verdict)) != null and
  (["acronym", "project-name", "proper-noun", "jargon", "phonetically-clear",
    "compound-clear", "stemming-artifact", "other"] | index($entry.category)) != null;

if ($expected | length) != 1 then error("expected one candidate document")
elif ($expected[0] | type) != "array" then error("expected a candidate array")
elif ($expected[0] | all(.[]; nonempty_string) and unique_terms | not)
then error("candidate terms must be nonempty unique strings")
elif length != 1 then error("expected one response document")
else
  .[0] as $response |
  if ($response | type) != "object" then error("response must be an object")
  elif ($response | keys) != ["terms"] then error("response requires only terms")
  elif ($response.terms | type) != "array" then error("terms must be an array")
  elif ($response.terms | all(.[]; valid_term) | not)
  then error("invalid classification schema")
  elif ($response.terms | map(.term) | unique_terms | not)
  then error("duplicate classification terms")
  elif ($response.terms | map(.term) | sort) != ($expected[0] | sort)
  then error("classification must cover exactly the candidate terms")
  else true end
end
