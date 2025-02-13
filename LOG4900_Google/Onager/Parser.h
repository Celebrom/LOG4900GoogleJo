/*
Copyright 2015 Google Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#pragma once
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include "Utils.h"
#include "Converter.h"
#include "LiveStack.h"
#include "../etw_reader/system_history.h"

class Parser
{
public:		
	static void parseStacks(SystemHistory& system_history, std::wstring path, std::ofstream& outputFile);
};