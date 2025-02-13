#include "LiveStack.h"
int LiveStack::idCounter = 1;

std::vector<std::string> LiveStack::GetFinalLines()
{
	return std::vector<std::string>();
}

std::vector<std::string> LiveStack::Update(base::History<Stack>::Element nextStack)
{
	lastTimestamp = nextStack.start_ts;
	Stack stack = nextStack.value;

	int iLive  = 0;
	int iStack = stack.size() - 1;
	int liveSize = lines.size();
	while (iLive < liveSize && iStack >= 0)
	{
		if (lines[iLive].GetName() != stack[iStack])
			break;

		++iLive; --iStack;
	}

	std::vector<std::string> completedFunctions;
	for (int i = iLive; i < liveSize; ++i)
	{
		lines[i].SetEndTimestamp(nextStack.start_ts);
		completedFunctions.push_back(lines[i].ToJson());
	}
	lines.erase(std::begin(lines) + iLive, std::end(lines));

	for (int i = iStack; i >= 0; --i)
	{
		int parentID = 0;
		if (lines.size() > 0)
			parentID = lines.back().GetID();
		lines.push_back(StackLine(idCounter++, stack[i], parentID, nextStack.start_ts));
	}

	return completedFunctions;
}