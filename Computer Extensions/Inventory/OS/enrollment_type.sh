#!/bin/bash

enrollType=$(profiles status -type enrollment | head -1)
echo "<result>$enrollType</result>"