import * as React from "react";
import styled from "styled-components/macro";
import { GaantChartExecutionPlanFragment } from "./types/GaantChartExecutionPlanFragment";
import { IRunMetadataDict, IStepState } from "../RunMetadataProvider";
import { RunFragment } from "../runs/types/RunFragment";
import { Spinner, Colors } from "@blueprintjs/core";
import { GaantChartMode } from "./Constants";
import { boxStyleFor } from "./GaantChartLayout";
import { formatElapsedTime } from "../Util";

interface GaantStatusPanelProps {
  plan: GaantChartExecutionPlanFragment;
  metadata: IRunMetadataDict;
  run?: RunFragment;

  onApplyStepFilter?: (step: string) => void;
  onHighlightStep?: (step: string | null) => void;
}

export const GaantStatusPanel: React.FunctionComponent<GaantStatusPanelProps> = ({
  metadata,
  onApplyStepFilter,
  onHighlightStep
}) => {
  const executing = Object.keys(metadata.steps).filter(
    key => metadata.steps[key].state === IStepState.RUNNING
  );
  const errored = Object.keys(metadata.steps).filter(
    key => metadata.steps[key].state === IStepState.FAILED
  );
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
      <SectionHeader>Executing</SectionHeader>
      <Section>
        {executing.map(stepName => (
          <StepItem
            name={stepName}
            key={stepName}
            metadata={metadata}
            onClick={() => onApplyStepFilter?.(stepName)}
          />
        ))}
      </Section>
      {executing.length === 0 && (
        <EmptyNotice>No steps are executing</EmptyNotice>
      )}
      <SectionHeader>Errored</SectionHeader>
      <Section>
        {errored.map(stepName => (
          <StepItem
            name={stepName}
            key={stepName}
            metadata={metadata}
            onClick={onApplyStepFilter}
            onHover={onHighlightStep}
          />
        ))}
      </Section>
    </div>
  );
};

const StepItem: React.FunctionComponent<{
  name: string;
  metadata: IRunMetadataDict;
  onClick?: (name: string) => void;
  onHover?: (name: string | null) => void;
}> = ({ name, metadata, onClick, onHover }) => {
  const step = metadata.steps[name];
  return (
    <StepItemContainer
      key={name}
      onClick={() => onClick?.(name)}
      onMouseEnter={() => onHover?.(name)}
      onMouseLeave={() => onHover?.(null)}
    >
      {step.state === IStepState.RUNNING ? (
        <Spinner size={15} />
      ) : (
        <StepStatusDot
          style={{
            ...boxStyleFor(name, {
              metadata,
              options: { mode: GaantChartMode.WATERFALL_TIMED }
            })
          }}
        />
      )}
      <StepLabel>{name}</StepLabel>
      <Elapsed>
        {formatElapsedTime(metadata.mostRecentLogAt - step.start!)}
      </Elapsed>
    </StepItemContainer>
  );
};

const SectionHeader = styled.div`
  font-size: 11px;
  padding: 3px 6px;
  text-transform: uppercase;
  background: ${Colors.LIGHT_GRAY4};
  border-bottom: 1px solid ${Colors.LIGHT_GRAY1};
  color: ${Colors.GRAY3};
  height: 20px;
`;

const Section = styled.div`
  overflow-y: auto;
`;

const StepLabel = styled.div`
  margin-left: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
`;

const StepItemContainer = styled.div`
  display: flex;
  line-height: 28px;
  height: 28px;
  padding: 0 5px;
  align-items: center;
  border-bottom: 1px solid ${Colors.LIGHT_GRAY1};
  font-size: 13px;

  &:hover {
    background: ${Colors.LIGHT_GRAY3};
  }
`;

const StepStatusDot = styled.div`
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  border-radius: 7.5px;
`;

const Elapsed = styled.div`
  color: ${Colors.GRAY3};
`;

const EmptyNotice = styled.div`
  padding: 7px 24px;
  font-size: 13px;
`;
