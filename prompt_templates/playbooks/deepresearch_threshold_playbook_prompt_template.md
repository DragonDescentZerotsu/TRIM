You are doing literature-grounded deep research to build a task-specific molecular-property playbook.

Task:
TDC {{TASK_DESCRIPTION}}

Goal:
Build a practical playbook for the task above, covering as many of the scientifically meaningful molecular properties used in this task as possible.

Important context:
- Your job is to find literature-supported threshold anchors, cutoffs, ranges, or commonly used interpretive rules for the provided molecular properties, specifically in the context of this task or the closest scientifically relevant neighboring tasks.
- We care about practical thresholds that chemists, ADMET researchers, or medicinal chemistry literature actually use, not only descriptor definitions.
- The property list below already uses human-readable names. Use those names directly in the playbook.
- In addition to numeric properties, if there are especially important functional groups that are repeatedly associated with the task outcome, record them in a separate qualitative section. Functional groups usually do not need thresholds or numeric ranges.

Molecular properties to cover:
{{FEATURE_LIST}}

Requirements:
1. Prioritize task-specific literature. If unavailable, use the closest neighboring domain and explicitly label it as a proxy.
2. For each molecular property, try to find the most commonly used literature threshold(s), cutoff(s), or heuristic range(s).
3. Keep the answer concise. We want a practical playbook, not a long review.
4. If the literature is conflicting, briefly note the main alternatives instead of forcing a single threshold.
5. If no reliable threshold exists, say so explicitly and give only a short qualitative note.
6. Do not invent thresholds.
7. Use primary sources or strong reviews whenever possible.
8. For the functional-group section, include only groups with fairly clear task relevance. Do not try to list every possible group.

Output format:
Produce a short playbook with one section per molecular property, using exactly this schema:

## {property_name}
- Common threshold(s) or range(s):
- Usually associated with:
- Brief note:
- Source:

If no reliable threshold exists, use:
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with:
- Brief note:
- Source:

After the property sections, add one more section using exactly this schema:

## Functional-group notes

For each clearly task-relevant functional group, add:
- Group name:
- Usually associated with:
- Brief note:
- Source:

If no clearly task-relevant functional group pattern is supported, write:
- Group name: no stable task-specific functional-group pattern found
- Usually associated with:
- Brief note:
- Source:
